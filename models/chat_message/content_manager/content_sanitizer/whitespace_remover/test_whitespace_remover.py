"""Tests for whitespace removal components"""
import pytest
from models.chat_message.content_manager.content_sanitizer.whitespace_remover import (
    ExtraSpaceTrimmer, SpaceTrimConfig,
    LineBreakCleaner, LineBreakConfig
)

class TestExtraSpaceTrimmer:
    @pytest.fixture
    def config(self):
        return SpaceTrimConfig(
            trim_edges=True,
            max_consecutive_spaces=1,
            preserve_indentation=False,
            preserve_paragraph_breaks=True
        )
        
    @pytest.fixture
    def trimmer(self, config):
        return ExtraSpaceTrimmer(config)
        
    def test_basic_trimming(self, trimmer):
        """Test basic space trimming"""
        text = "  Too   many    spaces  "
        result, stats = trimmer.trim_spaces(text)
        assert result == "Too many spaces"
        assert stats["spaces_removed"] > 0
        assert stats["edges_trimmed"] > 0
        
    def test_preserve_paragraphs(self, trimmer):
        """Test paragraph preservation"""
        text = "Paragraph 1\n\nParagraph 2"
        result, _ = trimmer.trim_spaces(text)
        assert result == text
        
    def test_indentation_handling(self, trimmer):
        """Test indentation handling"""
        trimmer.config.preserve_indentation = True
        text = "    Indented line\n    Still indented"
        result, _ = trimmer.trim_spaces(text)
        assert result == text

class TestLineBreakCleaner:
    @pytest.fixture
    def config(self):
        return LineBreakConfig(
            max_consecutive_breaks=2,
            normalize_line_endings=True,
            preserve_markdown_breaks=True,
            preserve_code_blocks=True
        )
        
    @pytest.fixture
    def cleaner(self, config):
        return LineBreakCleaner(config)
        
    def test_basic_cleaning(self, cleaner):
        """Test basic line break cleaning"""
        text = "Line 1\n\n\n\nLine 2"
        result, stats = cleaner.clean_breaks(text)
        assert result == "Line 1\n\nLine 2"
        assert stats["breaks_removed"] > 0
        
    def test_markdown_breaks(self, cleaner):
        """Test markdown break preservation"""
        text = "Line 1  \nLine 2"
        result, _ = cleaner.clean_breaks(text)
        assert result == text
        
    def test_code_block_preservation(self, cleaner):
        """Test code block preservation"""
        text = "Normal text\n```\ndef code():\n    pass\n```\nMore text"
        result, _ = cleaner.clean_breaks(text)
        assert "```" in result
        assert "def code():" in result