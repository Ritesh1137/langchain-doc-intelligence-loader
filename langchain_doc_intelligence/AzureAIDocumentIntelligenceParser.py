import logging
from typing import Any, Iterator, List, Optional

from langchain_core.documents import Document

from langchain_community.document_loaders.base import BaseBlobParser
from langchain_community.document_loaders.blob_loaders import Blob

import markdown
from bs4 import BeautifulSoup
import re

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
        lines = md_content.split('\n')
        tables = []
        current_table = []
        in_table = False
        for i, line in enumerate(lines):
            if '|' in line:  # Check if the line might be part of a table
                if not in_table:  # Starting a new table
                    in_table = True
                    current_table = [line]
                else:  # Continuing an existing table
                    current_table.append(line)
            else:
                if in_table:  # End of a table, check for caption
                    in_table = False
                    # Assume the line immediately after a table could be a caption, 
                    # especially if it's not empty and not another markdown table start
                    potential_caption = lines[i + 1] if i + 1 < len(lines) else ""
                    # Basic heuristic to decide if the following line is a caption:
                    # - It shouldn't contain table syntax.
                    # - It should be a non-empty line.
                    # - Adjust based on your markdown patterns.
                    if potential_caption and not potential_caption.startswith('|'):
                        caption = potential_caption.strip()
                        i += 1  # Skip over the caption line in the next iteration
                    else:
                        caption = None
                    tables.append({'content': "\n".join(current_table), 'caption': caption})
                    current_table = []

        # Handle the case where a document ends with a table
        if in_table:
            tables.append({'content': "\n".join(current_table), 'caption': None})

        return tables


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
        
        table_count = self.count_markdown_tables(final_content)
        yield Document(page_content=final_content, metadata={"table_count": table_count})


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