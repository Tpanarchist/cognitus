"""Tests for profanity filter components"""
import pytest
from models.chat_message.content_manager.content_sanitizer.profanity_filter import (
    BlacklistLoader, BlacklistConfig, ProfanityReplacer, ReplacementConfig
)

class TestBlacklistLoader:
    @pytest.fixture
    def blacklist_config(self):
        return BlacklistConfig(
            default_blacklist={"bad", "worse"},
            custom_blacklist={"custom_bad"},
            case_sensitive=False
        )
        
    @pytest.fixture
    def loader(self, blacklist_config):
        return BlacklistLoader(blacklist_config)
        
    def test_initialization(self, loader):
        """Test blacklist initialization"""
        blacklist = loader.get_blacklist()
        assert "bad" in blacklist
        assert "worse" in blacklist
        assert "custom_bad" in blacklist
        
    def test_case_sensitivity(self):
        """Test case sensitivity configuration"""
        config = BlacklistConfig(
            default_blacklist={"Bad"},
            case_sensitive=True
        )
        loader = BlacklistLoader(config)
        
        assert loader.is_blacklisted("Bad")
        assert not loader.is_blacklisted("bad")
        
    def test_add_remove_words(self, loader):
        """Test adding and removing words"""
        loader.add_words({"new_bad"})
        assert loader.is_blacklisted("new_bad")
        
        loader.remove_words({"new_bad"})
        assert not loader.is_blacklisted("new_bad")

class TestProfanityReplacer:
    @pytest.fixture
    def blacklist_config(self):
        return BlacklistConfig(
            default_blacklist={"bad", "worse"},
            case_sensitive=False
        )
        
    @pytest.fixture
    def replacement_config(self):
        return ReplacementConfig(
            replacement_char="*",
            preserve_length=True,
            whole_words_only=True,
            custom_replacements={"bad": "good"}
        )
        
    @pytest.fixture
    def replacer(self, blacklist_config, replacement_config):
        return ProfanityReplacer(blacklist_config, replacement_config)
        
    def test_basic_replacement(self, replacer):
        """Test basic word replacement"""
        text = "This is bad and worse!"
        cleaned, stats = replacer.replace_profanity(text)
        assert cleaned == "This is good and ****!"
        assert stats["bad"] == 1
        assert stats["worse"] == 1
        
    def test_preserve_length(self, replacer):
        """Test length preservation"""
        replacer.config.custom_replacements = {}  # Clear custom replacements
        text = "This is bad!"
        cleaned, _ = replacer.replace_profanity(text)
        assert cleaned == "This is ***!"
        
    def test_whole_words_only(self, replacer):
        """Test whole word matching"""
        text = "badword isn't bad but worse is"
        cleaned, stats = replacer.replace_profanity(text)
        assert cleaned == "badword isn't good but ****! is"
        assert stats.get("bad") == 1
        assert stats.get("worse") == 1