"""Creates and manages message timestamps"""
from datetime import datetime, timezone
from typing import Optional, Dict
from pydantic import BaseModel

class TimestampConfig(BaseModel):
    """Configuration for timestamp creation"""
    use_utc: bool = True
    include_microseconds: bool = True
    include_metadata: bool = True
    track_intervals: bool = True

class TimestampMetadata(BaseModel):
    """Metadata for a timestamp"""
    unix_timestamp: float
    is_utc: bool
    has_timezone: bool
    microseconds: Optional[int] = None
    interval_data: Optional[Dict[str, float]] = None

class TimestampCreator:
    """Creates and manages message timestamps"""
    
    def __init__(self, config: Optional[TimestampConfig] = None):
        self.config = config or TimestampConfig()
        self._last_timestamp: Optional[datetime] = None
        
    def _create_base_timestamp(self) -> datetime:
        """Create base timestamp according to configuration"""
        if self.config.use_utc:
            timestamp = datetime.now(timezone.utc)
        else:
            timestamp = datetime.now().astimezone()
            
        if not self.config.include_microseconds:
            timestamp = timestamp.replace(microsecond=0)
            
        return timestamp
    
    def _create_metadata(
        self,
        timestamp: datetime,
        interval: Optional[float] = None
    ) -> TimestampMetadata:
        """Create metadata for timestamp"""
        metadata = TimestampMetadata(
            unix_timestamp=timestamp.timestamp(),
            is_utc=timestamp.tzinfo is timezone.utc,
            has_timezone=timestamp.tzinfo is not None,
            microseconds=timestamp.microsecond if self.config.include_microseconds else None
        )
        
        if interval is not None:
            metadata.interval_data = {
                "seconds_since_last": interval,
                "messages_per_second": 1/interval if interval > 0 else None
            }
            
        return metadata
    
    def create_timestamp(self) -> tuple[datetime, TimestampMetadata]:
        """
        Create a new timestamp with metadata
        
        Returns:
            Tuple of (timestamp, metadata)
        """
        timestamp = self._create_base_timestamp()
        
        interval = None
        if self.config.track_intervals and self._last_timestamp:
            interval = (timestamp - self._last_timestamp).total_seconds()
            
        metadata = self._create_metadata(timestamp, interval)
        self._last_timestamp = timestamp
        
        return timestamp, metadata