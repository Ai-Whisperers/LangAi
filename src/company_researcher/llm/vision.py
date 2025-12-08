"""
Vision Capabilities for Document Analysis.

Enables image analysis using Claude's vision capabilities for:
- Financial chart analysis
- Document OCR and extraction
- Logo and brand recognition
- Screenshot analysis

Usage:
    from company_researcher.llm.vision import get_vision_analyzer

    analyzer = get_vision_analyzer()

    # Analyze financial chart
    data = analyzer.analyze_financial_chart("chart.png")

    # Extract text from document
    text = analyzer.extract_text_from_document("document.png")

    # Custom analysis
    result = analyzer.analyze_image(
        image_source="screenshot.png",
        prompt="What company's website is this?"
    )
"""

from typing import Union, List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path
from threading import Lock
import base64
import json

from anthropic import Anthropic

from .client_factory import get_anthropic_client


@dataclass
class ImageAnalysisResult:
    """Result from image analysis."""
    content: str
    model: str
    input_tokens: int
    output_tokens: int
    image_tokens: int  # Estimated image tokens
    structured_data: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "model": self.model,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "image_tokens": self.image_tokens,
            "structured_data": self.structured_data
        }


class VisionAnalyzer:
    """
    Analyzes images and documents using Claude's vision capabilities.

    Supports:
    - Local files (PNG, JPG, GIF, WebP)
    - URLs
    - Base64 encoded data
    """

    # Supported image types
    SUPPORTED_TYPES = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.webp': 'image/webp'
    }

    def __init__(self, client: Optional[Anthropic] = None):
        """
        Initialize the vision analyzer.

        Args:
            client: Optional Anthropic client
        """
        self.client = client or get_anthropic_client()

    def analyze_image(
        self,
        image_source: Union[str, bytes, Path],
        prompt: str,
        model: str = "claude-sonnet-4-20250514",
        max_tokens: int = 1000,
        temperature: float = 0.0,
        system: Optional[str] = None
    ) -> ImageAnalysisResult:
        """
        Analyze an image with a custom prompt.

        Args:
            image_source: Image file path, URL, or bytes
            prompt: Analysis prompt
            model: Model to use
            max_tokens: Maximum response tokens
            temperature: Sampling temperature
            system: Optional system prompt

        Returns:
            ImageAnalysisResult object
        """
        image_content = self._prepare_image_content(image_source)

        messages = [{
            "role": "user",
            "content": [
                image_content,
                {"type": "text", "text": prompt}
            ]
        }]

        params = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages
        }

        if system:
            params["system"] = system

        response = self.client.messages.create(**params)

        # Estimate image tokens (rough approximation)
        # Claude charges ~765 tokens per 1000x1000 image region
        image_tokens = self._estimate_image_tokens(image_source)

        return ImageAnalysisResult(
            content=response.content[0].text,
            model=model,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            image_tokens=image_tokens
        )

    def analyze_multiple_images(
        self,
        image_sources: List[Union[str, bytes, Path]],
        prompt: str,
        model: str = "claude-sonnet-4-20250514",
        max_tokens: int = 2000,
        temperature: float = 0.0
    ) -> ImageAnalysisResult:
        """
        Analyze multiple images together.

        Args:
            image_sources: List of images
            prompt: Analysis prompt
            model: Model to use
            max_tokens: Maximum response tokens
            temperature: Sampling temperature

        Returns:
            ImageAnalysisResult object
        """
        content = []

        for i, source in enumerate(image_sources):
            image_content = self._prepare_image_content(source)
            content.append(image_content)
            content.append({"type": "text", "text": f"[Image {i+1}]"})

        content.append({"type": "text", "text": prompt})

        messages = [{"role": "user", "content": content}]

        response = self.client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=messages
        )

        total_image_tokens = sum(
            self._estimate_image_tokens(src) for src in image_sources
        )

        return ImageAnalysisResult(
            content=response.content[0].text,
            model=model,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            image_tokens=total_image_tokens
        )

    # =========================================================================
    # Specialized Analysis Methods
    # =========================================================================

    def analyze_financial_chart(
        self,
        image_source: Union[str, bytes, Path],
        model: str = "claude-sonnet-4-20250514"
    ) -> Dict[str, Any]:
        """
        Extract data from financial charts.

        Args:
            image_source: Chart image
            model: Model to use

        Returns:
            Structured chart data
        """
        prompt = """Analyze this financial chart and extract:

1. **Chart Type**: (line, bar, pie, candlestick, etc.)
2. **Title/Subject**: What is being measured
3. **Time Period**: Date range covered
4. **Data Points**: Key values with dates/labels
5. **Trends**: Direction and magnitude of changes
6. **Notable Features**: Peaks, troughs, anomalies

Format your response as JSON with these keys:
{
    "chart_type": "string",
    "title": "string",
    "time_period": {"start": "date", "end": "date"},
    "y_axis_label": "string",
    "data_points": [{"date": "string", "value": number, "label": "string"}],
    "trends": ["string"],
    "notable_features": ["string"],
    "summary": "string"
}"""

        result = self.analyze_image(
            image_source=image_source,
            prompt=prompt,
            model=model,
            max_tokens=1500
        )

        # Parse JSON from response
        try:
            # Find JSON in response
            content = result.content
            start = content.find('{')
            end = content.rfind('}') + 1
            if start >= 0 and end > start:
                result.structured_data = json.loads(content[start:end])
        except json.JSONDecodeError:
            result.structured_data = {"raw_analysis": result.content}

        return result.structured_data

    def extract_text_from_document(
        self,
        image_source: Union[str, bytes, Path],
        preserve_layout: bool = True,
        model: str = "claude-sonnet-4-20250514"
    ) -> str:
        """
        OCR-like text extraction from document images.

        Args:
            image_source: Document image
            preserve_layout: Whether to preserve formatting
            model: Model to use

        Returns:
            Extracted text
        """
        if preserve_layout:
            prompt = """Extract all text from this document image.

Preserve the original structure and formatting as much as possible:
- Maintain paragraph breaks
- Preserve bullet points and numbered lists
- Keep table structures using markdown tables
- Indicate headers with ## or ###
- Preserve any emphasized text

Output the extracted text:"""
        else:
            prompt = """Extract all text from this document image.
Output as plain text, combining paragraphs into continuous text.
Separate sections with blank lines."""

        result = self.analyze_image(
            image_source=image_source,
            prompt=prompt,
            model=model,
            max_tokens=4000
        )

        return result.content

    def extract_table_data(
        self,
        image_source: Union[str, bytes, Path],
        model: str = "claude-sonnet-4-20250514"
    ) -> Dict[str, Any]:
        """
        Extract table data from image.

        Args:
            image_source: Image containing table
            model: Model to use

        Returns:
            Structured table data
        """
        prompt = """Extract the table data from this image.

Return as JSON with:
{
    "headers": ["column1", "column2", ...],
    "rows": [
        ["cell1", "cell2", ...],
        ...
    ],
    "notes": "any additional context about the table"
}

Be precise with numbers and text. If a cell is empty, use null."""

        result = self.analyze_image(
            image_source=image_source,
            prompt=prompt,
            model=model,
            max_tokens=2000
        )

        try:
            content = result.content
            start = content.find('{')
            end = content.rfind('}') + 1
            if start >= 0 and end > start:
                return json.loads(content[start:end])
        except json.JSONDecodeError:
            pass

        return {"raw_extraction": result.content}

    def analyze_company_logo(
        self,
        image_source: Union[str, bytes, Path],
        model: str = "claude-sonnet-4-20250514"
    ) -> Dict[str, Any]:
        """
        Analyze company logo for brand information.

        Args:
            image_source: Logo image
            model: Model to use

        Returns:
            Brand analysis
        """
        prompt = """Analyze this company logo and provide:

1. **Company Name**: If recognizable
2. **Design Elements**: Colors, shapes, symbols
3. **Typography**: Font style if text is present
4. **Brand Impression**: Professional, playful, tech, etc.
5. **Industry Guess**: What industry might this company be in

Format as JSON:
{
    "company_name": "string or null",
    "colors": ["color1", "color2"],
    "design_style": "string",
    "has_text": boolean,
    "brand_impression": ["adjective1", "adjective2"],
    "likely_industry": "string",
    "similar_to": ["known brand if similar"]
}"""

        result = self.analyze_image(
            image_source=image_source,
            prompt=prompt,
            model=model,
            max_tokens=800
        )

        try:
            content = result.content
            start = content.find('{')
            end = content.rfind('}') + 1
            if start >= 0 and end > start:
                return json.loads(content[start:end])
        except json.JSONDecodeError:
            pass

        return {"raw_analysis": result.content}

    def analyze_screenshot(
        self,
        image_source: Union[str, bytes, Path],
        analysis_type: str = "general",
        model: str = "claude-sonnet-4-20250514"
    ) -> Dict[str, Any]:
        """
        Analyze website or app screenshot.

        Args:
            image_source: Screenshot image
            analysis_type: Type of analysis (general, ux, content, competitive)
            model: Model to use

        Returns:
            Screenshot analysis
        """
        prompts = {
            "general": """Analyze this screenshot and describe:
1. What application/website is shown
2. Main purpose of this page
3. Key features visible
4. Overall design quality
5. Any notable elements""",

            "ux": """Analyze this screenshot for UX quality:
1. Navigation clarity
2. Visual hierarchy
3. Call-to-action visibility
4. Information density
5. Accessibility considerations
6. Potential usability issues""",

            "content": """Extract content information from this screenshot:
1. Main headings and text
2. Key messages or value propositions
3. Products/services shown
4. Pricing information if visible
5. Contact or action items""",

            "competitive": """Analyze this competitor screenshot:
1. Company identification
2. Product/service offering
3. Pricing strategy hints
4. Unique selling points
5. Target audience indicators
6. Strengths and weaknesses"""
        }

        prompt = prompts.get(analysis_type, prompts["general"])

        result = self.analyze_image(
            image_source=image_source,
            prompt=prompt,
            model=model,
            max_tokens=1500
        )

        return {
            "analysis_type": analysis_type,
            "content": result.content,
            "model": model
        }

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def _prepare_image_content(
        self,
        image_source: Union[str, bytes, Path]
    ) -> Dict[str, Any]:
        """
        Prepare image content for API request.

        Args:
            image_source: Image source (path, URL, or bytes)

        Returns:
            Image content dictionary for API
        """
        # Handle URL
        if isinstance(image_source, str) and image_source.startswith(('http://', 'https://')):
            return {
                "type": "image",
                "source": {
                    "type": "url",
                    "url": image_source
                }
            }

        # Handle file path
        if isinstance(image_source, (str, Path)):
            path = Path(image_source)
            if not path.exists():
                raise FileNotFoundError(f"Image file not found: {path}")

            media_type = self._get_media_type(str(path))
            if media_type is None:
                raise ValueError(f"Unsupported image type: {path.suffix}")

            with open(path, 'rb') as f:
                image_data = base64.standard_b64encode(f.read()).decode('utf-8')

            return {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": media_type,
                    "data": image_data
                }
            }

        # Handle bytes
        if isinstance(image_source, bytes):
            image_data = base64.standard_b64encode(image_source).decode('utf-8')
            return {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/png",  # Default to PNG
                    "data": image_data
                }
            }

        raise ValueError(f"Unsupported image source type: {type(image_source)}")

    def _get_media_type(self, path: str) -> Optional[str]:
        """Get media type from file extension."""
        ext = Path(path).suffix.lower()
        return self.SUPPORTED_TYPES.get(ext)

    def _estimate_image_tokens(
        self,
        image_source: Union[str, bytes, Path]
    ) -> int:
        """
        Estimate token count for an image.

        Claude charges approximately 765 tokens per 1000x1000 pixel region.
        This is a rough estimate without actually loading image dimensions.
        """
        # Default estimate for a typical image
        # Actual token count depends on image dimensions
        return 1500  # Conservative estimate


# Singleton instance
_vision_analyzer: Optional[VisionAnalyzer] = None
_analyzer_lock = Lock()


def get_vision_analyzer() -> VisionAnalyzer:
    """
    Get singleton vision analyzer instance.

    Returns:
        VisionAnalyzer instance
    """
    global _vision_analyzer
    if _vision_analyzer is None:
        with _analyzer_lock:
            if _vision_analyzer is None:
                _vision_analyzer = VisionAnalyzer()
    return _vision_analyzer


def reset_vision_analyzer() -> None:
    """Reset vision analyzer instance (for testing)."""
    global _vision_analyzer
    _vision_analyzer = None
