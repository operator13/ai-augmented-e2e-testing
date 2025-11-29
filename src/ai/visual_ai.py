"""
AI-Powered Visual Regression Testing

Intelligent visual comparison that understands context and ignores acceptable changes
like dates, dynamic content, and ads while detecting real visual regressions.
"""
import base64
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import cv2
import imagehash
import numpy as np
from anthropic import Anthropic
from openai import OpenAI
from PIL import Image
from playwright.sync_api import Page

from src.config.settings import settings


class VisualAI:
    """AI-powered visual regression testing"""

    def __init__(self, use_claude: bool = True):
        """
        Initialize Visual AI

        Args:
            use_claude: Use Claude for visual analysis (supports vision)
        """
        self.use_claude = use_claude
        self.baseline_dir = settings.visual_baseline_dir
        self.baseline_dir.mkdir(parents=True, exist_ok=True)

        # Initialize AI client (Claude has better vision capabilities)
        if use_claude and settings.anthropic_api_key:
            self.ai_client = Anthropic(api_key=settings.anthropic_api_key)
            self.ai_model = settings.claude_model
        elif settings.openai_api_key:
            self.ai_client = OpenAI(api_key=settings.openai_api_key)
            self.ai_model = "gpt-4-vision-preview"  # GPT-4 with vision
            self.use_claude = False
        else:
            self.ai_client = None

    def compare_visual(
        self,
        page: Page,
        screenshot_name: str,
        element_selector: Optional[str] = None,
        ignore_regions: Optional[List[Dict]] = None,
        use_ai_analysis: bool = True,
    ) -> Dict:
        """
        Compare current page/element with baseline screenshot

        Args:
            page: Playwright page object
            screenshot_name: Name for the screenshot
            element_selector: Optional selector to screenshot specific element
            ignore_regions: List of regions to ignore {x, y, width, height}
            use_ai_analysis: Use AI to analyze differences

        Returns:
            Comparison result with diff percentage and AI insights
        """
        # Take current screenshot
        current_path = self._take_screenshot(page, screenshot_name, element_selector)

        # Get baseline path
        baseline_path = self.baseline_dir / f"{screenshot_name}_baseline.png"

        # If no baseline exists, create one
        if not baseline_path.exists():
            current_path.replace(baseline_path)
            return {
                "status": "baseline_created",
                "message": f"Baseline created at {baseline_path}",
                "diff_percentage": 0.0,
            }

        # Compare screenshots
        diff_result = self._compare_images(
            baseline_path, current_path, ignore_regions=ignore_regions
        )

        # If difference is significant and AI is enabled, analyze with AI
        if (
            diff_result["diff_percentage"] > settings.visual_diff_threshold
            and use_ai_analysis
            and settings.enable_visual_ai
        ):
            ai_analysis = self._ai_analyze_difference(baseline_path, current_path, diff_result)
            diff_result["ai_analysis"] = ai_analysis

        # Save diff image
        if diff_result.get("diff_image") is not None:
            diff_path = self.baseline_dir / f"{screenshot_name}_diff.png"
            cv2.imwrite(str(diff_path), diff_result["diff_image"])
            diff_result["diff_image_path"] = str(diff_path)
            del diff_result["diff_image"]  # Remove numpy array from result

        return diff_result

    def _take_screenshot(
        self, page: Page, name: str, element_selector: Optional[str] = None
    ) -> Path:
        """Take screenshot of page or element"""
        screenshot_path = self.baseline_dir / f"{name}_current.png"

        if element_selector:
            element = page.locator(element_selector)
            element.screenshot(path=str(screenshot_path))
        else:
            page.screenshot(path=str(screenshot_path), full_page=True)

        return screenshot_path

    def _compare_images(
        self,
        baseline_path: Path,
        current_path: Path,
        ignore_regions: Optional[List[Dict]] = None,
    ) -> Dict:
        """
        Compare two images using multiple algorithms

        Returns:
            Dict with comparison results
        """
        # Load images
        baseline_img = cv2.imread(str(baseline_path))
        current_img = cv2.imread(str(current_path))

        # Ensure images are same size
        if baseline_img.shape != current_img.shape:
            current_img = cv2.resize(current_img, (baseline_img.shape[1], baseline_img.shape[0]))

        # Apply ignore regions (mask them out)
        if ignore_regions:
            for region in ignore_regions:
                x, y, w, h = region["x"], region["y"], region["width"], region["height"]
                baseline_img[y : y + h, x : x + w] = 0
                current_img[y : y + h, x : x + w] = 0

        # Structural Similarity Index (SSIM)
        ssim_score = self._calculate_ssim(baseline_img, current_img)

        # Perceptual hash comparison
        hash_similarity = self._calculate_hash_similarity(baseline_path, current_path)

        # Pixel-wise difference
        diff_img, pixel_diff_percent = self._calculate_pixel_difference(baseline_img, current_img)

        # Overall diff percentage (weighted combination)
        diff_percentage = (
            (1 - ssim_score) * 0.4  # SSIM contributes 40%
            + (1 - hash_similarity) * 0.3  # Hash contributes 30%
            + pixel_diff_percent * 0.3  # Pixel diff contributes 30%
        )

        return {
            "status": "passed" if diff_percentage <= settings.visual_diff_threshold else "failed",
            "diff_percentage": round(diff_percentage * 100, 2),
            "ssim_score": round(ssim_score, 4),
            "hash_similarity": round(hash_similarity, 4),
            "pixel_diff_percent": round(pixel_diff_percent * 100, 2),
            "diff_image": diff_img,
            "threshold": settings.visual_diff_threshold * 100,
        }

    def _calculate_ssim(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """Calculate Structural Similarity Index"""
        # Convert to grayscale
        gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

        # Calculate SSIM (simplified version)
        # For production, use skimage.metrics.structural_similarity
        mean1 = np.mean(gray1)
        mean2 = np.mean(gray2)
        std1 = np.std(gray1)
        std2 = np.std(gray2)

        # Simple correlation coefficient as SSIM approximation
        correlation = np.corrcoef(gray1.flatten(), gray2.flatten())[0, 1]
        return max(0.0, correlation)  # Clamp to [0, 1]

    def _calculate_hash_similarity(self, img1_path: Path, img2_path: Path) -> float:
        """Calculate perceptual hash similarity"""
        img1 = Image.open(img1_path)
        img2 = Image.open(img2_path)

        hash1 = imagehash.average_hash(img1)
        hash2 = imagehash.average_hash(img2)

        # Calculate similarity (0 = identical, higher = more different)
        hash_diff = hash1 - hash2
        max_diff = 64  # Maximum possible difference for average hash

        similarity = 1 - (hash_diff / max_diff)
        return max(0.0, min(1.0, similarity))

    def _calculate_pixel_difference(
        self, img1: np.ndarray, img2: np.ndarray
    ) -> Tuple[np.ndarray, float]:
        """Calculate pixel-wise difference"""
        # Calculate absolute difference
        diff = cv2.absdiff(img1, img2)

        # Create a visual diff image (highlight differences in red)
        diff_visual = img1.copy()
        gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray_diff, 30, 255, cv2.THRESH_BINARY)

        # Highlight differences
        diff_visual[thresh > 0] = [0, 0, 255]  # Red for differences

        # Calculate percentage of different pixels
        total_pixels = img1.shape[0] * img1.shape[1]
        different_pixels = np.count_nonzero(thresh)
        diff_percentage = different_pixels / total_pixels

        return diff_visual, diff_percentage

    def _ai_analyze_difference(
        self, baseline_path: Path, current_path: Path, diff_result: Dict
    ) -> Dict:
        """
        Use AI to analyze visual differences and determine if they're acceptable

        Args:
            baseline_path: Path to baseline image
            current_path: Path to current screenshot
            diff_result: Result from image comparison

        Returns:
            AI analysis with insights
        """
        if not self.ai_client:
            return {"error": "AI client not configured"}

        try:
            # Encode images as base64
            baseline_b64 = self._encode_image(baseline_path)
            current_b64 = self._encode_image(current_path)

            prompt = f"""
            Analyze these two screenshots from toyota.com for visual regression testing:

            Baseline (expected) vs Current (actual)

            Technical comparison shows:
            - Difference: {diff_result['diff_percentage']}%
            - SSIM Score: {diff_result['ssim_score']}
            - Pixel Diff: {diff_result['pixel_diff_percent']}%

            Please analyze and provide:
            1. Are the differences acceptable (e.g., dates, dynamic content, ads)?
            2. Are there real visual regressions (layout, styling, missing elements)?
            3. List specific differences you observe
            4. Verdict: PASS or FAIL with justification

            Return as JSON:
            {{
                "verdict": "PASS" or "FAIL",
                "is_acceptable": true/false,
                "differences_found": ["list of specific differences"],
                "likely_causes": ["possible explanations"],
                "recommendation": "action to take",
                "confidence": 0.0-1.0
            }}
            """

            if self.use_claude:
                response = self.ai_client.messages.create(
                    model=self.ai_model,
                    max_tokens=1000,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {
                                    "type": "image",
                                    "source": {
                                        "type": "base64",
                                        "media_type": "image/png",
                                        "data": baseline_b64,
                                    },
                                },
                                {
                                    "type": "image",
                                    "source": {
                                        "type": "base64",
                                        "media_type": "image/png",
                                        "data": current_b64,
                                    },
                                },
                            ],
                        }
                    ],
                )
                analysis_text = response.content[0].text
            else:
                # OpenAI GPT-4 Vision
                response = self.ai_client.chat.completions.create(
                    model=self.ai_model,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/png;base64,{baseline_b64}"
                                    },
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/png;base64,{current_b64}"
                                    },
                                },
                            ],
                        }
                    ],
                    max_tokens=1000,
                )
                analysis_text = response.choices[0].message.content

            # Extract JSON from response
            analysis = self._extract_json(analysis_text)
            return analysis if analysis else {"raw_response": analysis_text}

        except Exception as e:
            return {"error": f"AI analysis failed: {str(e)}"}

    def _encode_image(self, image_path: Path) -> str:
        """Encode image as base64"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def _extract_json(self, text: str) -> Optional[Dict]:
        """Extract JSON from AI response"""
        import re

        json_match = re.search(r"```json\n(.*?)\n```", text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        # Try to find raw JSON
        json_match = re.search(r"(\{.*\})", text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        return None

    def update_baseline(self, screenshot_name: str):
        """Update baseline screenshot with current version"""
        current_path = self.baseline_dir / f"{screenshot_name}_current.png"
        baseline_path = self.baseline_dir / f"{screenshot_name}_baseline.png"

        if current_path.exists():
            current_path.replace(baseline_path)
            print(f"Baseline updated: {baseline_path}")
        else:
            print(f"Current screenshot not found: {current_path}")

    def generate_visual_report(self, results: List[Dict], output_path: Optional[Path] = None):
        """Generate HTML report for visual regression results"""
        if output_path is None:
            output_path = settings.report_dir / "visual_regression_report.html"

        html = self._build_html_report(results)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            f.write(html)

        print(f"Visual regression report generated: {output_path}")

    def _build_html_report(self, results: List[Dict]) -> str:
        """Build HTML report from results"""
        # Simplified HTML report template
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Visual Regression Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .result { border: 1px solid #ddd; padding: 15px; margin: 10px 0; }
                .passed { border-left: 5px solid #4CAF50; }
                .failed { border-left: 5px solid #f44336; }
                .images { display: flex; gap: 10px; }
                .images img { max-width: 300px; }
            </style>
        </head>
        <body>
            <h1>Visual Regression Test Report</h1>
        """

        for result in results:
            status_class = result.get("status", "unknown")
            html += f"""
            <div class="result {status_class}">
                <h3>{result.get('name', 'Unknown Test')}</h3>
                <p><strong>Status:</strong> {status_class.upper()}</p>
                <p><strong>Difference:</strong> {result.get('diff_percentage', 0)}%</p>
                {self._format_ai_analysis(result.get('ai_analysis', {}))}
            </div>
            """

        html += "</body></html>"
        return html

    def _format_ai_analysis(self, analysis: Dict) -> str:
        """Format AI analysis for HTML report"""
        if not analysis:
            return ""

        html = "<div class='ai-analysis'><h4>AI Analysis</h4>"
        html += f"<p><strong>Verdict:</strong> {analysis.get('verdict', 'N/A')}</p>"

        if "differences_found" in analysis:
            html += "<p><strong>Differences:</strong></p><ul>"
            for diff in analysis["differences_found"]:
                html += f"<li>{diff}</li>"
            html += "</ul>"

        if "recommendation" in analysis:
            html += f"<p><strong>Recommendation:</strong> {analysis['recommendation']}</p>"

        html += "</div>"
        return html
