import logging
from typing import Any, Iterator, List, Optional

from langchain_core.documents import Document

from langchain_community.document_loaders.base import BaseBlobParser
from langchain_community.document_loaders.blob_loaders import Blob

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
    def extract_tables_with_captions(md_content):
        lines = md_content.split('\n')
        tables = []
        current_table = []
        in_table = False
        header_stack = []
        current_metadata = {}

        for i, line in enumerate(lines):
            stripped_line = line.strip()

            # Header tracking
            if stripped_line.startswith('#'):
                header_level = stripped_line.count('#')
                header = stripped_line[header_level:].strip()
                header_stack = header_stack[:header_level]  # Reset stack at current level
                current_metadata = {f'level_{level}': name for level, name in header_stack}
                current_metadata['current_header'] = header  # Update current metadata
                header_stack.append((header_level, header))  # Push current header to stack

            # Table extraction
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
                    # Add table with metadata
                    tables.append({
                        'content': "\n".join(current_table),
                        'caption': caption,
                        # 'section': current_metadata.get(1, None),
                        # 'subsection': current_metadata.get(2, None)                        
                        'section': current_metadata.get('level_1'),  
                        'subsection': current_metadata.get('level_2') 
                    })
                    current_table = []

        # Handle the case where a document ends with a table
        if in_table:
            tables.append({
                'content': "\n".join(current_table),
                'caption': None,
                # 'section': current_metadata.get(1, None),
                # 'subsection': current_metadata.get(2, None)
                'section': current_metadata.get('level_1'),  
                'subsection': current_metadata.get('level_2') 
            })

        return tables

    
    @staticmethod
    def summarize_table(table_content, caption=None):

        intro = """
        This table, formatted in markdown, is extracted from a document and 
        can contain a variety of data types including numbers, text, sentences, 
        or any other kind of data.The table is intended to present information
        relevant to the document's overall context or specific sections within."""
        if caption:
            intro += f" The table's caption, '{caption},' provides additional context."        
       
        instructions = """
        IMPORTANT: Please ensure your analysis remains strictly confined ONLY to the data provided in the table. Do not refer to or assume any external context.
        Please analyze and summarize the key information presented in the table below. Your summary should:
        - Identify and highlight significant trends, patterns or values.
        - Note any particularly relevant data points, whether they are numerical values, text descriptions, or key sentences.
        - Make comparisons and contrasts between different columns or rows as necessary, elucidating any notable differences or similarities.
        - Directly interpret the data presented, focusing exclusively on the information within the table without referring to or assuming additional external context.
        The summary should be short, articulate, informative, and span 5-8 sentences, aiming for a comprehensive overview that accommodates the table's content.        
        """
        
        prompt = f"{intro}\n\nTable Content:\n{table_content}{instructions}"

        responses = openai.chat.completions.create(
            # model="gpt-3.5-turbo-0125",
            model="gpt-4-0125-preview",
            messages=[
                {"role": "system", "content": "You are a helpful table summarization assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            n=1,
            stop=None,
            temperature=0.0,
            )
        summaries = [choice.message.content for choice in responses.choices]        
        summary = " ".join(summaries)
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
        final_content = self.to_ascii(result.content)
        table_data = self.extract_tables_with_captions(final_content)
        enriched_summaries = []

        # Process each table to generate summaries and maintain associated metadata
        for table in table_data:
            table_content = table["content"]
            caption = table["caption"]
            section = table["section"]
            subsection = table["subsection"]

            # Generate the summary for the current table
            summary = self.summarize_table(table_content, caption)

            # Append the summary with its metadata
            enriched_summaries.append({
                'summary': summary,
                'caption': caption,
                'section': section,
                'subsection': subsection,
                'table_summary': True
            })

        # Yield a Document that includes all summaries with their metadata
        yield Document(
            page_content=final_content,
            metadata={
                'table_summaries': enriched_summaries
            }
        )


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