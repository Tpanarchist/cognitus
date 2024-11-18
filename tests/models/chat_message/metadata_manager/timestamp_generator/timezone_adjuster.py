"""Adjusts and converts timestamp timezones"""
from datetime import datetime, timezone, tzinfo
from typing import Optional, Dict, Union, List
from zoneinfo import ZoneInfo
from pydantic import BaseModel

class TimezoneConfig(BaseModel):
    """Configuration for timezone adjustment"""
    default_timezone: str = "UTC"
    preserve_original: bool = True
    track_conversions: bool = True

class TimezoneConversion(BaseModel):
    """Details of a timezone conversion"""
    from_zone: str
    to_zone: str
    offset_hours: float
    is_dst: bool
    original_timestamp: Optional[datetime] = None

class TimezoneAdjuster:
    """Adjusts and converts timestamp timezones"""
    
    def __init__(self, config: Optional[TimezoneConfig] = None):
        self.config = config or TimezoneConfig()
        self._conversion_history: List[TimezoneConversion] = []
        
    def _get_timezone(self, tz_name: Optional[str] = None) -> tzinfo:
        """Get timezone object from name"""
        try:
            return ZoneInfo(tz_name or self.config.default_timezone)
        except KeyError:
            return timezone.utc
            
    def _create_conversion_record(
        self,
        timestamp: datetime,
        from_tz: tzinfo,
        to_tz: tzinfo
    ) -> TimezoneConversion:
        """Create record of timezone conversion"""
        offset = (to_tz.utcoffset(None) - from_tz.utcoffset(None)).total_seconds() / 3600
        
        return TimezoneConversion(
            from_zone=str(from_tz),
            to_zone=str(to_tz),
            offset_hours=offset,
            is_dst=bool(to_tz.dst(timestamp)),
            original_timestamp=timestamp if self.config.preserve_original else None
        )
        
    def adjust_timezone(
        self,
        timestamp: datetime,
        target_timezone: Optional[str] = None
    ) -> tuple[datetime, TimezoneConversion]:
        """
        Adjust timestamp to target timezone
        
        Args:
            timestamp: Timestamp to adjust
            target_timezone: Target timezone name
            
        Returns:
            Tuple of (adjusted timestamp, conversion details)
        """
        # Get timezone objects
        from_tz = timestamp.tzinfo or timezone.utc
        to_tz = self._get_timezone(target_timezone)
        
        # Convert timestamp
        adjusted = timestamp.astimezone(to_tz)
        
        # Create conversion record
        conversion = self._create_conversion_record(timestamp, from_tz, to_tz)
        
        if self.config.track_conversions:
            self._conversion_history.append(conversion)
            
        return adjusted, conversion
    
    def get_conversion_history(self) -> List[TimezoneConversion]:
        """Get history of timezone conversions"""
        return self._conversion_history
    
    def is_same_instant(
        self,
        timestamp1: datetime,
        timestamp2: datetime
    ) -> bool:
        """Check if two timestamps represent the same instant"""
        return timestamp1.astimezone(timezone.utc) == timestamp2.astimezone(timezone.utc)