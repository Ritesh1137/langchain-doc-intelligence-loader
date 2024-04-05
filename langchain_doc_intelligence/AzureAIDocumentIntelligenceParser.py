import logging
from typing import Any, Iterator, List, Optional

from langchain_core.documents import Document

from langchain_community.document_loaders.base import BaseBlobParser
from langchain_community.document_loaders.blob_loaders import Blob

import markdown
from bs4 import BeautifulSoup
import re
import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


logger = logging.getLogger(__name__) 


class AzureAIDocumentIntelligenceParser(BaseBlobParser):
    """Loads a PDF with Azure Document Intelligence
    (formerly Forms Recognizer)."""

    def __init__(
        self,
        api_endpoint: str,
        api_key: str,
        api_version: Optional[str] = None,
        api_model: str = "prebuilt-layout",
        mode: str = "markdown",
        analysis_features: Optional[List[str]] = None,
    ):
        from azure.ai.documentintelligence import DocumentIntelligenceClient
        from azure.ai.documentintelligence.models import DocumentAnalysisFeature
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.documentintelligence.models import ContentFormat

        kwargs = {}
        if api_version is not None:
            kwargs["api_version"] = api_version

        if analysis_features is not None:
            _SUPPORTED_FEATURES = [
                DocumentAnalysisFeature.OCR_HIGH_RESOLUTION,
            ]

            analysis_features = [
                DocumentAnalysisFeature(feature) for feature in analysis_features
            ]
            if any(
                [feature not in _SUPPORTED_FEATURES for feature in analysis_features]
            ):
                logger.warning(
                    f"The current supported features are: "
                    f"{[f.value for f in _SUPPORTED_FEATURES]}. "
                    "Using other features may result in unexpected behavior."
                )

        self.client = DocumentIntelligenceClient(
            endpoint=api_endpoint,
            credential=AzureKeyCredential(api_key),
            headers={"x-ms-useragent": "langchain-parser/1.0.0"},
            features=analysis_features,
            **kwargs,
        )
        self.api_model = api_model
        self.mode = mode
        assert self.mode in ["single", "page", "markdown", "markdown-page"]

    @staticmethod
    def to_ascii(text):
        return text.encode('ascii', 'replace').decode()
    
    @staticmethod
    def count_markdown_tables(md_content):
        lines = md_content.split('\n')
        table_count = 0
        found_separator = False

        for line in lines:
            trimmed_line = line.strip()
            if '|' in trimmed_line:
                # Split the line by pipe characters and strip whitespace from each segment
                segments = [seg.strip() for seg in trimmed_line.split('|') if seg.strip()]
                # Check if all segments of the line are either dashes (possibly with colons for alignment) or empty
                if all(s == '-' * len(s) or s.replace(':', '') == '-' * len(s.replace(':', '')) for s in segments):
                    if not found_separator:  # This checks if it's the first separator line of a table
                        table_count += 1
                        found_separator = True
                else:
                    found_separator = False  # Not a separator line, reset flag
            else:
                found_separator = False  # Line without pipes, reset flag

        return table_count
    
    @staticmethod
    def extract_tables_with_captions(md_content):
        '''
        Extracts tables and their immediate captions from a markdown string.

        This function identifies tables in a markdown-formatted string based on the
        presence of "|" characters denoting table rows. It assumes that a caption,
        if present, follows immediately after the table. The function returns a list
        of dictionaries, each containing the 'content' of a table and its 'caption'.
        If a table does not have a caption, the 'caption' field is set to None.

        Parameters:
        - md_content (str): A string containing markdown content.

        Returns:
        - List[dict]: A list where each element is a dictionary with keys 'content'
        (the markdown table as a string) and 'caption' (the text immediately following
        the table, or None if there is no caption).
        '''
        lines = md_content.split('\n')
        tables = []
        current_table = []
        in_table = False
        for i, line in enumerate(lines):
            if '|' in line:  
                if not in_table:  
                    in_table = True
                    current_table = [line]
                else:  
                    current_table.append(line)
            else:
                if in_table:  
                    in_table = False                    
                    potential_caption = lines[i + 1] if i + 1 < len(lines) else ""                   
                    if potential_caption and not potential_caption.startswith('|'):
                        caption = potential_caption.strip()
                        i += 1  
                    else:
                        caption = None
                    tables.append({'content': "\n".join(current_table), 'caption': caption})
                    current_table = []

        # Handle the case where a document ends with a table
        if in_table:
            tables.append({'content': "\n".join(current_table), 'caption': None})

        return tables
    
    @staticmethod
    def summarize_table(table_content, caption=None):
        prompt = f"Table Content:\n{table_content}"
        if caption:
            prompt += f"\n\nCaption: {caption}"
        prompt += "\n\nSummarize the key information in this table in 5-6 sentences:"

        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful table summarization assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            n=1,
            stop=None,
            temperature=0,
            )
        # summary = response.choices[0].text.strip()
        summary = response
        # summaries = [completion.choices[0].message.content for completion in response]

        return summary


    def _generate_docs_page(self, result: Any) -> Iterator[Document]:
        for p in result.pages:
            content = " ".join([line.content for line in p.lines])

            d = Document(
                page_content=content,
                metadata={
                    "page": p.page_number,
                },
            )
            yield d
    
    def _generate_docs_markdown_page(self, result: Any) -> Iterator[Document]:
        table_summaries = []      
        final_content = self.to_ascii(result.content)
        
        table_count = self.count_markdown_tables(final_content)

        table_data = self.extract_tables_with_captions(final_content)
        for table in table_data:
            table_content = table["content"]
            caption = table["caption"]
            summary = self.summarize_table(table_content, caption)
            # chat_completion_response = self.summarize_table(table_content, caption)
            table_summaries.append(summary)

            # for completion in chat_completion_response:
            #     summary_text = completion.choices[0].message.content
            #     table_summaries.append(summary_text)

        # combined_summaries = " ".join(table_summaries)
        yield Document(
            page_content=final_content,
            metadata={
                "table_count": table_count,
                "table_summaries": table_summaries
            })


    def _generate_docs_single(self, result: Any) -> Iterator[Document]:
        yield Document(page_content=result.content, metadata={})

    def lazy_parse(self, blob: Blob) -> Iterator[Document]:
        """Lazily parse the blob."""

        with blob.as_bytes_io() as file_obj:
            poller = self.client.begin_analyze_document(
                self.api_model,
                file_obj,
                content_type="application/octet-stream",
                output_content_format=ContentFormat.MARKDOWN if self.mode in ["markdown", "markdown-page"] else ContentFormat.TEXT,
            )
            result = poller.result()

            if self.mode in ["single", "markdown"]:
                yield from self._generate_docs_single(result)
            elif self.mode in ["page"]:
                yield from self._generate_docs_page(result)
            elif self.mode in ["markdown-page"]:
                yield from self._generate_docs_markdown_page(result)
            else:
                raise ValueError(f"Invalid mode: {self.mode}")


    def parse_url(self, url: str) -> Iterator[Document]:
        from azure.ai.documentintelligence.models import AnalyzeDocumentRequest

        poller = self.client.begin_analyze_document(
            self.api_model,
            AnalyzeDocumentRequest(url_source=url),
            # content_type="application/octet-stream",
            output_content_format="markdown" if self.mode in ["markdown", "markdown-page"] else "text",
        )
        result = poller.result()

        if self.mode in ["single", "markdown"]:
            yield from self._generate_docs_single(result)
        elif self.mode in ["page"]:
            yield from self._generate_docs_page(result)
        elif self.mode in ["markdown-page"]:
            yield from self._generate_docs_markdown_page(result)
        else:
            raise ValueError(f"Invalid mode: {self.mode}")