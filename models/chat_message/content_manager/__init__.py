"""
Content management components for message handling.

This module provides comprehensive content handling capabilities including:
- Raw and processed text storage
- Content sanitization and filtering
- Content formatting and tone adjustment
- Emoji processing
"""
from typing import Optional

# Text Content Storage Components
from .text_content_holder import (
    RawContent,
    RawContentStorer,
    ProcessedContent,
    ContentModification,
    ProcessedContentStorer
)

# Content Sanitization Components
from .content_sanitizer.profanity_filter import (
    BlacklistConfig,
    BlacklistLoader,
    ReplacementConfig,
    ProfanityReplacer
)

from .content_sanitizer.whitespace_remover import (
    SpaceTrimConfig,
    ExtraSpaceTrimmer,
    LineBreakConfig,
    LineBreakCleaner
)

from .content_sanitizer.punctuation_normalizer import (
    StandardizationConfig,
    PunctuationStandardizer,
    ExcessConfig,
    ExcessPunctuationRemover
)

# Content Formatting Components
from .content_formatter.formality_adjuster import (
    CasualFormality,
    CasualFormalitySetter,
    FormalFormality,
    FormalFormalitySetter
)

from .content_formatter.tone_polarity_adjuster import (
    PositiveToneConfig,
    PositiveToneApplier,
    NegativeToneConfig,
    NegativeToneApplier
)

# Emoji Processing Components
from .emoji_handler import (
    EmojiConfig,
    EmojiExtractor,
    FormatterConfig as EmojiFormatterConfig,
    EmojiFormatter
)

class ContentManager:
    """Coordinates content processing and management"""
    
    def __init__(
        self,
        profanity_config: Optional[BlacklistConfig] = None,
        replacement_config: Optional[ReplacementConfig] = None,
        whitespace_config: Optional[SpaceTrimConfig] = None,
        linebreak_config: Optional[LineBreakConfig] = None,
        punctuation_config: Optional[StandardizationConfig] = None,
        excess_config: Optional[ExcessConfig] = None,
        emoji_config: Optional[EmojiConfig] = None,
        emoji_formatter_config: Optional[EmojiFormatterConfig] = None
    ):
        # Initialize content storage
        self.raw_storer = RawContentStorer()
        self.processed_storer = ProcessedContentStorer()
        
        # Initialize sanitizers
        self.profanity_filter = ProfanityReplacer(
            profanity_config,
            replacement_config
        )
        self.space_trimmer = ExtraSpaceTrimmer(whitespace_config)
        self.break_cleaner = LineBreakCleaner(linebreak_config)
        self.punct_standardizer = PunctuationStandardizer(punctuation_config)
        self.punct_remover = ExcessPunctuationRemover(excess_config)
        
        # Initialize formatters
        self.casual_setter = CasualFormalitySetter()
        self.formal_setter = FormalFormalitySetter()
        self.positive_applier = PositiveToneApplier()
        self.negative_applier = NegativeToneApplier()
        
        # Initialize emoji handlers
        self.emoji_extractor = EmojiExtractor(emoji_config)
        self.emoji_formatter = EmojiFormatter(emoji_formatter_config)
    
    def process_content(
        self,
        content: str,
        sanitize: bool = True,
        formality: Optional[str] = None,
        tone: Optional[str] = None,
        process_emoji: bool = True
    ) -> ProcessedContent:
        """
        Process message content through configured handlers
        
        Args:
            content: Raw content to process
            sanitize: Whether to apply content sanitization
            formality: Optional formality adjustment ("casual" or "formal")
            tone: Optional tone adjustment ("positive" or "negative")
            process_emoji: Whether to process emoji
            
        Returns:
            ProcessedContent object containing processed content and modifications
        """
        # Store raw content
        raw_content = self.raw_storer.store_content(content)
        result = content
        
        # Apply sanitization if configured
        if sanitize:
            # Profanity filtering
            cleaned, _ = self.profanity_filter.replace_profanity(result)
            result = self.processed_storer.store_content(
                cleaned,
                raw_content.content,
                "profanity_filter"
            )
            
            # Whitespace cleaning
            cleaned, _ = self.space_trimmer.trim_spaces(result.content)
            cleaned, _ = self.break_cleaner.clean_breaks(cleaned)
            result = self.processed_storer.add_modification(
                result,
                cleaned,
                "whitespace_clean"
            )
            
            # Punctuation normalization
            cleaned, _ = self.punct_standardizer.standardize(result.content)
            cleaned, _ = self.punct_remover.remove_excess(cleaned)
            result = self.processed_storer.add_modification(
                result,
                cleaned,
                "punctuation_clean"
            )
            
        # Apply formality adjustment if requested
        if formality == "casual":
            casual, _ = self.casual_setter.set_casual_formality(result.content)
            result = self.processed_storer.add_modification(
                result,
                casual,
                "casual_formality"
            )
        elif formality == "formal":
            formal, _ = self.formal_setter.set_formal_formality(result.content)
            result = self.processed_storer.add_modification(
                result,
                formal,
                "formal_formality"
            )
            
        # Apply tone adjustment if requested
        if tone == "positive":
            positive, _ = self.positive_applier.apply_positive_tone(result.content)
            result = self.processed_storer.add_modification(
                result,
                positive,
                "positive_tone"
            )
        elif tone == "negative":
            negative, _ = self.negative_applier.apply_negative_tone(result.content)
            result = self.processed_storer.add_modification(
                result,
                negative,
                "negative_tone"
            )
            
        # Process emoji if configured
        if process_emoji:
            emoji_info = self.emoji_extractor.extract_emoji(result.content)
            formatted = self.emoji_formatter.format_emoji(result.content)
            result = self.processed_storer.add_modification(
                result,
                formatted,
                "emoji_process",
                {"emoji_data": emoji_info}
            )
            
        return self.processed_storer.mark_complete(result)

__all__ = [
    # Main Manager
    "ContentManager",
    
    # Storage Components
    "RawContent",
    "RawContentStorer",
    "ProcessedContent",
    "ContentModification",
    "ProcessedContentStorer",
    
    # Sanitization Components
    "BlacklistConfig",
    "BlacklistLoader",
    "ReplacementConfig",
    "ProfanityReplacer",
    "SpaceTrimConfig", 
    "ExtraSpaceTrimmer",
    "LineBreakConfig",
    "LineBreakCleaner",
    "StandardizationConfig",
    "PunctuationStandardizer",
    "ExcessConfig",
    "ExcessPunctuationRemover",
    
    # Formatting Components
    "CasualFormality",
    "CasualFormalitySetter",
    "FormalFormality",
    "FormalFormalitySetter",
    "PositiveToneConfig",
    "PositiveToneApplier",
    "NegativeToneConfig",
    "NegativeToneApplier",
    
    # Emoji Components
    "EmojiConfig",
    "EmojiExtractor",
    "EmojiFormatterConfig",
    "EmojiFormatter"
]