"""Tests for punctuation normalization components"""
import pytest
from models.chat_message.content_manager.content_sanitizer.punctuation_normalizer import (
    PunctuationStandardizer,
    StandardizationConfig,
    ExcessPunctuationRemover,
    ExcessConfig
)

class TestPunctuationStandardizer:
    @pytest.fixture
    def config(self):
        return StandardizationConfig(
            punctuation_map={
                '"': '"',
                '"': '"',
                "'": "'",
                '—': '-',
                '…': '...',
            },
            preserve_quotes_in_code=True,
            standardize_ellipsis=True,
            fix_spacing=True
        )
    
    @pytest.fixture
    def standardizer(self, config):
        return PunctuationStandardizer(config)
    
    def test_quote_standardization(self, standardizer):
        """Test standardization of quotes"""
        text = '"Hello" and "world"'
        result, stats = standardizer.standardize(text)
        assert result == '"Hello" and "world"'
        assert stats['"'] == 2
        assert stats['"'] == 2
    
    def test_dash_standardization(self, standardizer):
        """Test standardization of dashes"""
        text = "Hello—world"
        result, stats = standardizer.standardize(text)
        assert result == "Hello-world"
        assert stats['—'] == 1
    
    def test_ellipsis_standardization(self, standardizer):
        """Test standardization of ellipsis"""
        text = "Hello… world..."
        result, stats = standardizer.standardize(text)
        assert result == "Hello... world..."
    
    def test_code_preservation(self, standardizer):
        """Test preservation of code blocks"""
        text = 'Regular "quote" and `code "quote"`'
        result, _ = standardizer.standardize(text)
        assert 'code "quote"' in result
    
    def test_spacing_fixes(self, standardizer):
        """Test fixing of punctuation spacing"""
        text = "Hello , world ! How are you ?"
        result, _ = standardizer.standardize(text)
        assert result == "Hello, world! How are you?"
    
    def test_multiple_punctuation_types(self, standardizer):
        """Test handling multiple punctuation types"""
        text = '"Hello"—how are you… feeling?'
        result, stats = standardizer.standardize(text)
        assert result == '"Hello"-how are you... feeling?'
        assert sum(stats.values()) > 0

class TestExcessPunctuationRemover:
    @pytest.fixture
    def config(self):
        return ExcessConfig(
            max_consecutive={
                '!': 3,
                '?': 2,
                '.': 3,
                '-': 2,
            },
            preserve_markdown=True,
            preserve_urls=True,
            preserve_code=True
        )
    
    @pytest.fixture
    def remover(self, config):
        return ExcessPunctuationRemover(config)
    
    def test_basic_excess_removal(self, remover):
        """Test basic removal of excess punctuation"""
        text = "Hello!!!!!!"
        result, stats = remover.remove_excess(text)
        assert result == "Hello!!!"
        assert stats['!'] == 4  # Removed 4 excess marks
    
    def test_multiple_punctuation_types(self, remover):
        """Test handling multiple punctuation types"""
        text = "What???!!!!!"
        result, stats = remover.remove_excess(text)
        assert result == "What??!!!"
        assert stats['?'] > 0
        assert stats['!'] > 0
    
    def test_preserve_code_blocks(self, remover):
        """Test preservation of code blocks"""
        text = "Normal!!!! `code!!!!` Normal!!!!"
        result, _ = remover.remove_excess(text)
        assert result == "Normal!!! `code!!!!` Normal!!!"
    
    def test_preserve_urls(self, remover):
        """Test preservation of URLs"""
        text = "Check http://example.com/path/??? !!!!!"
        result, _ = remover.remove_excess(text)
        assert "http://example.com/path/???" in result
        assert result.endswith("!!!")
    
    def test_preserve_markdown(self, remover):
        """Test preservation of markdown syntax"""
        text = "**Bold!!!** Normal!!!!"
        result, _ = remover.remove_excess(text)
        assert "**Bold!!!**" in result
        assert result.endswith("!!!")
    
    def test_consecutive_different_punctuation(self, remover):
        """Test handling consecutive different punctuation marks"""
        text = "Really??!!??!!"
        result, stats = remover.remove_excess(text)
        assert result == "Really??!!!"
        assert stats['?'] > 0
        assert stats['!'] > 0

    def test_ellipsis_preservation(self, remover):
        """Test proper handling of ellipsis"""
        text = "And so...... more text"
        result, stats = remover.remove_excess(text)
        assert result == "And so... more text"
        assert stats['.'] > 0
    
    def test_special_content_combination(self, remover):
        """Test handling combination of special content"""
        text = (
            "Check this **bold!!!** and `code!!!!` "
            "and https://test.com/??? and *italic!!!*"
        )
        result, _ = remover.remove_excess(text)
        assert "**bold!!!**" in result
        assert "`code!!!!`" in result
        assert "https://test.com/???" in result
        assert "*italic!!!*" in result