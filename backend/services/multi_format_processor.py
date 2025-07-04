#!/usr/bin/env python3
"""
Multi-Format Input Processing Service for Catalyst
Handles various conversation formats and data sources with advanced parsing capabilities
"""

import asyncio
import logging
import os
try:
    from typing import List, Dict, Any, Optional, Union, Tuple
    from datetime import datetime, timedelta, timezone
    import json
    import re
    import csv
    import io
    from dataclasses import dataclass, asdict
    from enum import Enum
except ImportError:
    pass

# Configure logging
logger = logging.getLogger(__name__)

class InputFormat(str, Enum):
    """Supported input formats"""
    WHATSAPP_EXPORT = "whatsapp_export"
    MESSENGER_JSON = "messenger_json"
    DISCORD_JSON = "discord_json"
    SLACK_JSON = "slack_json"
    TEAMS_EXPORT = "teams_export"
    TELEGRAM_JSON = "telegram_json"
    SMS_BACKUP = "sms_backup"
    EMAIL_MBOX = "email_mbox"
    CSV_GENERIC = "csv_generic"
    JSON_GENERIC = "json_generic"
    TEXT_TRANSCRIPT = "text_transcript"
    AUDIO_FILE = "audio_file"
    IMAGE_SCREENSHOT = "image_screenshot"
    PDF_DOCUMENT = "pdf_document"
    REAL_TIME_STREAM = "real_time_stream"

class ProcessingMode(str, Enum):
    """Processing modes for different use cases"""
    BATCH = "batch"
    STREAMING = "streaming"
    REAL_TIME = "real_time"
    INCREMENTAL = "incremental"

@dataclass
class ProcessedMessage:
    """Standardized message format after processing"""
    id: str
    sender: str
    content: str
    timestamp: datetime
    platform: str
    message_type: str = "text"
    metadata: Optional[Dict[str, Any]] = None
    attachments: Optional[List[Dict[str, Any]]] = None
    reactions: Optional[List[Dict[str, Any]]] = None
    thread_id: Optional[str] = None
    reply_to: Optional[str] = None
    edited: bool = False
    deleted: bool = False
    confidence_score: float = 1.0

@dataclass
class ProcessingResult:
    """Result of multi-format processing"""
    messages: List[ProcessedMessage]
    metadata: Dict[str, Any]
    format_detected: InputFormat
    processing_stats: Dict[str, Any]
    errors: List[str]
    warnings: List[str]
    confidence_score: float
    participants: List[str]
    date_range: Tuple[datetime, datetime]
    total_messages: int
    processing_time: float

class MultiFormatProcessor:
    """Advanced multi-format input processor"""
    
    def __init__(self):
        self.format_detectors = {
            InputFormat.WHATSAPP_EXPORT: self._detect_whatsapp,
            InputFormat.MESSENGER_JSON: self._detect_messenger,
            InputFormat.DISCORD_JSON: self._detect_discord,
            InputFormat.SLACK_JSON: self._detect_slack,
            InputFormat.TEAMS_EXPORT: self._detect_teams,
            InputFormat.TELEGRAM_JSON: self._detect_telegram,
            InputFormat.SMS_BACKUP: self._detect_sms,
            InputFormat.EMAIL_MBOX: self._detect_email,
            InputFormat.CSV_GENERIC: self._detect_csv,
            InputFormat.JSON_GENERIC: self._detect_json,
            InputFormat.TEXT_TRANSCRIPT: self._detect_text,
            InputFormat.AUDIO_FILE: self._detect_audio,
            InputFormat.IMAGE_SCREENSHOT: self._detect_image,
            InputFormat.PDF_DOCUMENT: self._detect_pdf,
        }
        
        self.format_processors = {
            InputFormat.WHATSAPP_EXPORT: self._process_whatsapp,
            InputFormat.MESSENGER_JSON: self._process_messenger,
            InputFormat.DISCORD_JSON: self._process_discord,
            InputFormat.SLACK_JSON: self._process_slack,
            InputFormat.TEAMS_EXPORT: self._process_teams,
            InputFormat.TELEGRAM_JSON: self._process_telegram,
            InputFormat.SMS_BACKUP: self._process_sms,
            InputFormat.EMAIL_MBOX: self._process_email,
            InputFormat.CSV_GENERIC: self._process_csv,
            InputFormat.JSON_GENERIC: self._process_json,
            InputFormat.TEXT_TRANSCRIPT: self._process_text,
            InputFormat.AUDIO_FILE: self._process_audio,
            InputFormat.IMAGE_SCREENSHOT: self._process_image,
            InputFormat.PDF_DOCUMENT: self._process_pdf,
        }
    
    async def process_input(self, 
                          input_data: Union[str, bytes, Dict[str, Any]], 
                          filename: Optional[str] = None,
                          format_hint: Optional[InputFormat] = None,
                          processing_mode: ProcessingMode = ProcessingMode.BATCH) -> ProcessingResult:
        """Process input data in various formats"""
        start_time = datetime.now(timezone.utc)
        
        try:
            # Detect format if not provided
            if format_hint:
                detected_format = format_hint
                confidence = 1.0
            else:
                detected_format, confidence = await self._detect_format(input_data, filename)
            
            logger.info(f"Processing input as {detected_format} (confidence: {confidence:.2f})")
            
            # Process based on detected format
            processor = self.format_processors.get(detected_format)
            if not processor:
                raise ValueError(f"No processor available for format: {detected_format}")
            
            messages, metadata, errors, warnings = await processor(input_data, processing_mode)
            
            # Calculate processing stats
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            participants = list(set(msg.sender for msg in messages if msg.sender))
            
            if messages:
                date_range = (
                    min(msg.timestamp for msg in messages),
                    max(msg.timestamp for msg in messages)
                )
            else:
                date_range = (start_time, start_time)
            
            processing_stats = {
                "processing_time_seconds": processing_time,
                "messages_processed": len(messages),
                "participants_found": len(participants),
                "date_range_days": (date_range[1] - date_range[0]).days,
                "format_confidence": confidence,
                "errors_count": len(errors),
                "warnings_count": len(warnings)
            }
            
            return ProcessingResult(
                messages=messages,
                metadata=metadata,
                format_detected=detected_format,
                processing_stats=processing_stats,
                errors=errors,
                warnings=warnings,
                confidence_score=confidence,
                participants=participants,
                date_range=date_range,
                total_messages=len(messages),
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Error processing input: {e}")
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            return ProcessingResult(
                messages=[],
                metadata={},
                format_detected=InputFormat.TEXT_TRANSCRIPT,
                processing_stats={"processing_time_seconds": processing_time},
                errors=[str(e)],
                warnings=[],
                confidence_score=0.0,
                participants=[],
                date_range=(start_time, start_time),
                total_messages=0,
                processing_time=processing_time
            )
    
    async def _detect_format(self, input_data: Union[str, bytes, Dict[str, Any]], 
                           filename: Optional[str] = None) -> Tuple[InputFormat, float]:
        """Detect input format with confidence score"""
        best_format = InputFormat.TEXT_TRANSCRIPT
        best_confidence = 0.0
        
        # Check filename extension first
        if filename:
            ext_format, ext_confidence = self._detect_by_extension(filename)
            if ext_confidence > best_confidence:
                best_format = ext_format
                best_confidence = ext_confidence
        
        # Check content-based detection
        for format_type, detector in self.format_detectors.items():
            try:
                confidence = await detector(input_data)
                if confidence > best_confidence:
                    best_format = format_type
                    best_confidence = confidence
            except Exception as e:
                logger.debug(f"Error in {format_type} detector: {e}")
        
        return best_format, best_confidence
    
    def _detect_by_extension(self, filename: str) -> Tuple[InputFormat, float]:
        """Detect format by file extension"""
        ext = Path(filename).suffix.lower()
        
        extension_map = {
            '.txt': (InputFormat.WHATSAPP_EXPORT, 0.6),
            '.json': (InputFormat.JSON_GENERIC, 0.7),
            '.csv': (InputFormat.CSV_GENERIC, 0.8),
            '.wav': (InputFormat.AUDIO_FILE, 0.9),
            '.mp3': (InputFormat.AUDIO_FILE, 0.9),
            '.m4a': (InputFormat.AUDIO_FILE, 0.9),
            '.png': (InputFormat.IMAGE_SCREENSHOT, 0.8),
            '.jpg': (InputFormat.IMAGE_SCREENSHOT, 0.8),
            '.jpeg': (InputFormat.IMAGE_SCREENSHOT, 0.8),
            '.pdf': (InputFormat.PDF_DOCUMENT, 0.9),
            '.mbox': (InputFormat.EMAIL_MBOX, 0.9),
        }
        
        return extension_map.get(ext, (InputFormat.TEXT_TRANSCRIPT, 0.1))
    
    # Format Detection Methods
    async def _detect_whatsapp(self, data: Union[str, bytes, Dict]) -> float:
        """Detect WhatsApp export format"""
        if isinstance(data, str):
            # Look for WhatsApp export patterns
            patterns = [
                r'\d{1,2}/\d{1,2}/\d{2,4}, \d{1,2}:\d{2} [AP]M - ',
                r'\[\d{1,2}/\d{1,2}/\d{2,4}, \d{1,2}:\d{2}:\d{2} [AP]M\]',
                r'Messages and calls are end-to-end encrypted',
                r'You created group'
            ]
            
            matches = sum(1 for pattern in patterns if re.search(pattern, data[:1000]))
            return min(matches * 0.3, 1.0)
        return 0.0
    
    async def _detect_messenger(self, data: Union[str, bytes, Dict]) -> float:
        """Detect Facebook Messenger JSON format"""
        if isinstance(data, dict) or (isinstance(data, str) and data.strip().startswith('{')):
            try:
                if isinstance(data, str):
                    data = json.loads(data)
                
                messenger_keys = ['participants', 'messages', 'thread_path', 'thread_type']
                matches = sum(1 for key in messenger_keys if key in data)
                return min(matches * 0.25, 1.0)
            except:
                pass
        return 0.0
    
    async def _detect_discord(self, data: Union[str, bytes, Dict]) -> float:
        """Detect Discord JSON export format"""
        if isinstance(data, dict) or (isinstance(data, str) and data.strip().startswith('{')):
            try:
                if isinstance(data, str):
                    data = json.loads(data)
                
                discord_keys = ['guild', 'channel', 'messages', 'messageCount']
                matches = sum(1 for key in discord_keys if key in data)
                return min(matches * 0.25, 1.0)
            except:
                pass
        return 0.0
    
    async def _detect_slack(self, data: Union[str, bytes, Dict]) -> float:
        """Detect Slack JSON export format"""
        if isinstance(data, list) or (isinstance(data, str) and data.strip().startswith('[')):
            try:
                if isinstance(data, str):
                    data = json.loads(data)
                
                if isinstance(data, list) and len(data) > 0:
                    first_item = data[0]
                    slack_keys = ['type', 'user', 'text', 'ts']
                    matches = sum(1 for key in slack_keys if key in first_item)
                    return min(matches * 0.25, 1.0)
            except:
                pass
        return 0.0
    
    async def _detect_teams(self, data: Union[str, bytes, Dict]) -> float:
        """Detect Microsoft Teams export format"""
        if isinstance(data, str):
            teams_patterns = [
                r'Microsoft Teams chat export',
                r'\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{2}:\d{2} [AP]M',
                r'<at>.*</at>'
            ]
            
            matches = sum(1 for pattern in teams_patterns if re.search(pattern, data[:1000]))
            return min(matches * 0.33, 1.0)
        return 0.0
    
    async def _detect_telegram(self, data: Union[str, bytes, Dict]) -> float:
        """Detect Telegram JSON export format"""
        if isinstance(data, dict) or (isinstance(data, str) and data.strip().startswith('{')):
            try:
                if isinstance(data, str):
                    data = json.loads(data)
                
                telegram_keys = ['name', 'type', 'id', 'messages']
                matches = sum(1 for key in telegram_keys if key in data)
                
                # Check for Telegram-specific message structure
                if 'messages' in data and isinstance(data['messages'], list):
                    if len(data['messages']) > 0:
                        msg = data['messages'][0]
                        if 'date' in msg and 'from' in msg:
                            matches += 1
                
                return min(matches * 0.2, 1.0)
            except:
                pass
        return 0.0
    
    async def _detect_sms(self, data: Union[str, bytes, Dict]) -> float:
        """Detect SMS backup format"""
        if isinstance(data, str):
            sms_patterns = [
                r'SMS Backup',
                r'<sms protocol=',
                r'address="\+\d+"',
                r'type="[12]"'
            ]
            
            matches = sum(1 for pattern in sms_patterns if re.search(pattern, data[:1000]))
            return min(matches * 0.25, 1.0)
        return 0.0
    
    async def _detect_email(self, data: Union[str, bytes, Dict]) -> float:
        """Detect email mbox format"""
        if isinstance(data, str):
            email_patterns = [
                r'^From \S+@\S+ ',
                r'Message-ID: <',
                r'Content-Type: ',
                r'Subject: '
            ]
            
            matches = sum(1 for pattern in email_patterns if re.search(pattern, data[:1000], re.MULTILINE))
            return min(matches * 0.25, 1.0)
        return 0.0
    
    async def _detect_csv(self, data: Union[str, bytes, Dict]) -> float:
        """Detect CSV format"""
        if isinstance(data, str):
            try:
                # Try to parse as CSV
                reader = csv.reader(io.StringIO(data[:1000]))
                rows = list(reader)
                
                if len(rows) >= 2:  # Header + at least one data row
                    # Check for common conversation CSV headers
                    headers = [h.lower() for h in rows[0]]
                    conversation_headers = ['timestamp', 'sender', 'message', 'content', 'text', 'date', 'time']
                    matches = sum(1 for header in conversation_headers if any(h in header for h in headers))
                    return min(matches * 0.2, 1.0)
            except:
                pass
        return 0.0
    
    async def _detect_json(self, data: Union[str, bytes, Dict]) -> float:
        """Detect generic JSON format"""
        try:
            if isinstance(data, str):
                json.loads(data)
                return 0.5  # Generic JSON gets medium confidence
            elif isinstance(data, dict):
                return 0.5
        except:
            pass
        return 0.0
    
    async def _detect_text(self, data: Union[str, bytes, Dict]) -> float:
        """Detect plain text transcript"""
        if isinstance(data, str):
            # Look for conversation patterns
            patterns = [
                r'^\w+: ',  # Speaker: message format
                r'\[\d{2}:\d{2}\]',  # Timestamp format
                r'\d{1,2}:\d{2} [AP]M',  # Time format
                r'\w+ says:',  # "Name says:" format
            ]
            
            matches = sum(1 for pattern in patterns if re.search(pattern, data[:1000], re.MULTILINE))
            return min(matches * 0.2 + 0.1, 1.0)  # Always has some confidence as fallback
        return 0.1
    
    async def _detect_audio(self, data: Union[str, bytes, Dict]) -> float:
        """Detect audio file format"""
        if isinstance(data, bytes):
            # Check audio file headers
            audio_headers = [
                b'RIFF',  # WAV
                b'ID3',   # MP3
                b'ftyp',  # M4A/MP4
                b'OggS',  # OGG
            ]
            
            for header in audio_headers:
                if data[:10].find(header) != -1:
                    return 0.9
        return 0.0
    
    async def _detect_image(self, data: Union[str, bytes, Dict]) -> float:
        """Detect image file format"""
        if isinstance(data, bytes):
            # Check image file headers
            image_headers = [
                (b'\xFF\xD8\xFF', 0.9),  # JPEG
                (b'\x89PNG\r\n\x1a\n', 0.9),  # PNG
                (b'GIF8', 0.9),  # GIF
                (b'BM', 0.8),  # BMP
            ]
            
            for header, confidence in image_headers:
                if data.startswith(header):
                    return confidence
        return 0.0
    
    async def _detect_pdf(self, data: Union[str, bytes, Dict]) -> float:
        """Detect PDF format"""
        if isinstance(data, bytes):
            if data.startswith(b'%PDF-'):
                return 0.9
        elif isinstance(data, str):
            if data.startswith('%PDF-'):
                return 0.9
        return 0.0
    
    # Format Processing Methods
    async def _process_whatsapp(self, data: str, mode: ProcessingMode) -> Tuple[List[ProcessedMessage], Dict, List[str], List[str]]:
        """Process WhatsApp export format"""
        messages = []
        errors = []
        warnings = []
        
        # WhatsApp export patterns
        patterns = [
            r'(\d{1,2}/\d{1,2}/\d{2,4}), (\d{1,2}:\d{2} [AP]M) - ([^:]+): (.+)',
            r'\[(\d{1,2}/\d{1,2}/\d{2,4}), (\d{1,2}:\d{2}:\d{2} [AP]M)\] ([^:]+): (.+)'
        ]
        
        lines = data.split('\n')
        current_message = None
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            matched = False
            for pattern in patterns:
                match = re.match(pattern, line)
                if match:
                    if current_message:
                        messages.append(current_message)
                    
                    try:
                        date_str, time_str, sender, content = match.groups()
                        
                        # Parse timestamp
                        timestamp_str = f"{date_str} {time_str}"
                        timestamp = self._parse_whatsapp_timestamp(timestamp_str)
                        
                        current_message = ProcessedMessage(
                            id=f"whatsapp_{i}",
                            sender=sender.strip(),
                            content=content.strip(),
                            timestamp=timestamp,
                            platform="whatsapp",
                            metadata={"line_number": i}
                        )
                        matched = True
                        break
                    except Exception as e:
                        errors.append(f"Error parsing line {i}: {e}")
            
            if not matched and current_message:
                # Continuation of previous message
                current_message.content += "\n" + line
        
        if current_message:
            messages.append(current_message)
        
        metadata = {
            "platform": "whatsapp",
            "export_type": "text",
            "total_lines": len(lines),
            "processed_messages": len(messages)
        }
        
        return messages, metadata, errors, warnings
    
    def _parse_whatsapp_timestamp(self, timestamp_str: str) -> datetime:
        """Parse WhatsApp timestamp formats"""
        formats = [
            "%m/%d/%y, %I:%M %p",
            "%d/%m/%y, %I:%M %p",
            "%m/%d/%Y, %I:%M %p",
            "%d/%m/%Y, %I:%M %p",
            "%m/%d/%y, %I:%M:%S %p",
            "%d/%m/%y, %I:%M:%S %p",
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(timestamp_str, fmt)
            except ValueError:
                continue
        
        # Fallback
        return datetime.now(timezone.utc)
    
    async def _process_messenger(self, data: Union[str, Dict], mode: ProcessingMode) -> Tuple[List[ProcessedMessage], Dict, List[str], List[str]]:
        """Process Facebook Messenger JSON format"""
        messages = []
        errors = []
        warnings = []
        
        try:
            if isinstance(data, str):
                data = json.loads(data)
            
            participants = [p.get('name', 'Unknown') for p in data.get('participants', [])]
            
            for i, msg in enumerate(data.get('messages', [])):
                try:
                    processed_msg = ProcessedMessage(
                        id=f"messenger_{i}",
                        sender=msg.get('sender_name', 'Unknown'),
                        content=msg.get('content', ''),
                        timestamp=datetime.fromtimestamp(msg.get('timestamp_ms', 0) / 1000),
                        platform="messenger",
                        metadata={
                            "type": msg.get('type', 'Generic'),
                            "reactions": msg.get('reactions', []),
                            "photos": msg.get('photos', []),
                            "videos": msg.get('videos', [])
                        }
                    )
                    
                    if processed_msg.content or msg.get('photos') or msg.get('videos'):
                        messages.append(processed_msg)
                    
                except Exception as e:
                    errors.append(f"Error processing message {i}: {e}")
            
            metadata = {
                "platform": "messenger",
                "participants": participants,
                "thread_type": data.get('thread_type', 'Unknown'),
                "thread_path": data.get('thread_path', ''),
                "total_messages": len(data.get('messages', []))
            }
            
        except Exception as e:
            errors.append(f"Error parsing Messenger data: {e}")
            metadata = {"platform": "messenger", "error": str(e)}
        
        return messages, metadata, errors, warnings
    
    async def _process_discord(self, data: Union[str, Dict], mode: ProcessingMode) -> Tuple[List[ProcessedMessage], Dict, List[str], List[str]]:
        """Process Discord JSON export format"""
        messages = []
        errors = []
        warnings = []
        
        try:
            if isinstance(data, str):
                data = json.loads(data)
            
            for i, msg in enumerate(data.get('messages', [])):
                try:
                    # Parse Discord timestamp
                    timestamp_str = msg.get('timestamp', '')
                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    
                    processed_msg = ProcessedMessage(
                        id=msg.get('id', f"discord_{i}"),
                        sender=msg.get('author', {}).get('name', 'Unknown'),
                        content=msg.get('content', ''),
                        timestamp=timestamp,
                        platform="discord",
                        metadata={
                            "author_id": msg.get('author', {}).get('id'),
                            "channel_id": msg.get('channelId'),
                            "attachments": msg.get('attachments', []),
                            "embeds": msg.get('embeds', []),
                            "reactions": msg.get('reactions', [])
                        }
                    )
                    
                    messages.append(processed_msg)
                    
                except Exception as e:
                    errors.append(f"Error processing Discord message {i}: {e}")
            
            metadata = {
                "platform": "discord",
                "guild": data.get('guild', {}),
                "channel": data.get('channel', {}),
                "message_count": data.get('messageCount', 0)
            }
            
        except Exception as e:
            errors.append(f"Error parsing Discord data: {e}")
            metadata = {"platform": "discord", "error": str(e)}
        
        return messages, metadata, errors, warnings
    
    async def _process_slack(self, data: Union[str, List], mode: ProcessingMode) -> Tuple[List[ProcessedMessage], Dict, List[str], List[str]]:
        """Process Slack JSON export format"""
        messages = []
        errors = []
        warnings = []
        
        try:
            if isinstance(data, str):
                data = json.loads(data)
            
            for i, msg in enumerate(data):
                try:
                    # Parse Slack timestamp
                    ts = float(msg.get('ts', 0))
                    timestamp = datetime.fromtimestamp(ts)
                    
                    processed_msg = ProcessedMessage(
                        id=f"slack_{ts}",
                        sender=msg.get('user', msg.get('username', 'Unknown')),
                        content=msg.get('text', ''),
                        timestamp=timestamp,
                        platform="slack",
                        metadata={
                            "type": msg.get('type'),
                            "subtype": msg.get('subtype'),
                            "thread_ts": msg.get('thread_ts'),
                            "files": msg.get('files', []),
                            "reactions": msg.get('reactions', [])
                        }
                    )
                    
                    messages.append(processed_msg)
                    
                except Exception as e:
                    errors.append(f"Error processing Slack message {i}: {e}")
            
            metadata = {
                "platform": "slack",
                "total_messages": len(data)
            }
            
        except Exception as e:
            errors.append(f"Error parsing Slack data: {e}")
            metadata = {"platform": "slack", "error": str(e)}
        
        return messages, metadata, errors, warnings
    
    async def _process_teams(self, data: str, mode: ProcessingMode) -> Tuple[List[ProcessedMessage], Dict, List[str], List[str]]:
        """Process Microsoft Teams export format"""
        messages = []
        errors = []
        warnings = []
        
        # Teams export pattern
        pattern = r'(\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{2}:\d{2} [AP]M) - ([^:]+): (.+)'
        
        lines = data.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            match = re.match(pattern, line)
            if match:
                try:
                    timestamp_str, sender, content = match.groups()
                    timestamp = datetime.strptime(timestamp_str, "%m/%d/%Y %I:%M:%S %p")
                    
                    processed_msg = ProcessedMessage(
                        id=f"teams_{i}",
                        sender=sender.strip(),
                        content=content.strip(),
                        timestamp=timestamp,
                        platform="teams",
                        metadata={"line_number": i}
                    )
                    
                    messages.append(processed_msg)
                    
                except Exception as e:
                    errors.append(f"Error processing Teams message {i}: {e}")
        
        metadata = {
            "platform": "teams",
            "total_lines": len(lines),
            "processed_messages": len(messages)
        }
        
        return messages, metadata, errors, warnings
    
    async def _process_telegram(self, data: Union[str, Dict], mode: ProcessingMode) -> Tuple[List[ProcessedMessage], Dict, List[str], List[str]]:
        """Process Telegram JSON export format"""
        messages = []
        errors = []
        warnings = []
        
        try:
            if isinstance(data, str):
                data = json.loads(data)
            
            for i, msg in enumerate(data.get('messages', [])):
                try:
                    # Parse Telegram timestamp
                    date_str = msg.get('date', '')
                    timestamp = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    
                    # Handle different message content types
                    content = ''
                    if isinstance(msg.get('text'), str):
                        content = msg['text']
                    elif isinstance(msg.get('text'), list):
                        content = ''.join(str(item) if isinstance(item, str) else item.get('text', '') 
                                        for item in msg['text'])
                    
                    processed_msg = ProcessedMessage(
                        id=msg.get('id', f"telegram_{i}"),
                        sender=msg.get('from', 'Unknown'),
                        content=content,
                        timestamp=timestamp,
                        platform="telegram",
                        metadata={
                            "type": msg.get('type'),
                            "media_type": msg.get('media_type'),
                            "file": msg.get('file'),
                            "photo": msg.get('photo'),
                            "forwarded_from": msg.get('forwarded_from')
                        }
                    )
                    
                    messages.append(processed_msg)
                    
                except Exception as e:
                    errors.append(f"Error processing Telegram message {i}: {e}")
            
            metadata = {
                "platform": "telegram",
                "chat_name": data.get('name', ''),
                "chat_type": data.get('type', ''),
                "chat_id": data.get('id', ''),
                "total_messages": len(data.get('messages', []))
            }
            
        except Exception as e:
            errors.append(f"Error parsing Telegram data: {e}")
            metadata = {"platform": "telegram", "error": str(e)}
        
        return messages, metadata, errors, warnings
    
    async def _process_sms(self, data: str, mode: ProcessingMode) -> Tuple[List[ProcessedMessage], Dict, List[str], List[str]]:
        """Process SMS backup XML format"""
        messages = []
        errors = []
        warnings = []
        
        try:
            import xml.etree.ElementTree as ET
            root = ET.fromstring(data)
            
            for i, sms in enumerate(root.findall('sms')):
                try:
                    timestamp = datetime.fromtimestamp(int(sms.get('date', 0)) / 1000)
                    
                    processed_msg = ProcessedMessage(
                        id=f"sms_{i}",
                        sender=sms.get('address', 'Unknown'),
                        content=sms.get('body', ''),
                        timestamp=timestamp,
                        platform="sms",
                        metadata={
                            "type": "sent" if sms.get('type') == '2' else "received",
                            "read": sms.get('read') == '1',
                            "contact_name": sms.get('contact_name')
                        }
                    )
                    
                    messages.append(processed_msg)
                    
                except Exception as e:
                    errors.append(f"Error processing SMS {i}: {e}")
            
            metadata = {
                "platform": "sms",
                "backup_format": "xml",
                "total_messages": len(root.findall('sms'))
            }
            
        except Exception as e:
            errors.append(f"Error parsing SMS data: {e}")
            metadata = {"platform": "sms", "error": str(e)}
        
        return messages, metadata, errors, warnings
    
    async def _process_email(self, data: str, mode: ProcessingMode) -> Tuple[List[ProcessedMessage], Dict, List[str], List[str]]:
        """Process email mbox format"""
        messages = []
        errors = []
        warnings = []
        
        try:
            import email
            from email import policy
            
            # Split mbox into individual messages
            email_messages = data.split('\nFrom ')[1:]  # Skip first empty split
            
            for i, email_text in enumerate(email_messages):
                try:
                    # Add back the From line
                    email_text = 'From ' + email_text
                    
                    msg = email.message_from_string(email_text, policy=policy.default)
                    
                    # Extract timestamp
                    date_str = msg.get('Date', '')
                    timestamp = email.utils.parsedate_to_datetime(date_str) if date_str else datetime.now(timezone.utc)
                    
                    # Extract content
                    content = ''
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == 'text/plain':
                                content = part.get_content()
                                break
                    else:
                        content = msg.get_content()
                    
                    processed_msg = ProcessedMessage(
                        id=f"email_{i}",
                        sender=msg.get('From', 'Unknown'),
                        content=content or '',
                        timestamp=timestamp,
                        platform="email",
                        metadata={
                            "subject": msg.get('Subject', ''),
                            "to": msg.get('To', ''),
                            "cc": msg.get('Cc', ''),
                            "message_id": msg.get('Message-ID', '')
                        }
                    )
                    
                    messages.append(processed_msg)
                    
                except Exception as e:
                    errors.append(f"Error processing email {i}: {e}")
            
            metadata = {
                "platform": "email",
                "format": "mbox",
                "total_messages": len(email_messages)
            }
            
        except Exception as e:
            errors.append(f"Error parsing email data: {e}")
            metadata = {"platform": "email", "error": str(e)}
        
        return messages, metadata, errors, warnings
    
    async def _process_csv(self, data: str, mode: ProcessingMode) -> Tuple[List[ProcessedMessage], Dict, List[str], List[str]]:
        """Process generic CSV format"""
        messages = []
        errors = []
        warnings = []
        
        try:
            reader = csv.DictReader(io.StringIO(data))
            
            # Try to map common column names
            column_mapping = self._detect_csv_columns(reader.fieldnames)
            
            for i, row in enumerate(reader):
                try:
                    # Extract timestamp
                    timestamp_str = row.get(column_mapping.get('timestamp', ''), '')
                    timestamp = self._parse_flexible_timestamp(timestamp_str) if timestamp_str else datetime.now(timezone.utc)
                    
                    processed_msg = ProcessedMessage(
                        id=f"csv_{i}",
                        sender=row.get(column_mapping.get('sender', ''), 'Unknown'),
                        content=row.get(column_mapping.get('content', ''), ''),
                        timestamp=timestamp,
                        platform="csv",
                        metadata={"row_number": i, "original_row": row}
                    )
                    
                    messages.append(processed_msg)
                    
                except Exception as e:
                    errors.append(f"Error processing CSV row {i}: {e}")
            
            metadata = {
                "platform": "csv",
                "columns": list(reader.fieldnames) if reader.fieldnames else [],
                "column_mapping": column_mapping,
                "total_rows": len(messages)
            }
            
        except Exception as e:
            errors.append(f"Error parsing CSV data: {e}")
            metadata = {"platform": "csv", "error": str(e)}
        
        return messages, metadata, errors, warnings
    
    def _detect_csv_columns(self, fieldnames: List[str]) -> Dict[str, str]:
        """Detect CSV column mapping"""
        if not fieldnames:
            return {}
        
        fieldnames_lower = [f.lower() for f in fieldnames]
        mapping = {}
        
        # Timestamp columns
        timestamp_candidates = ['timestamp', 'date', 'time', 'datetime', 'created_at', 'sent_at']
        for candidate in timestamp_candidates:
            for i, field in enumerate(fieldnames_lower):
                if candidate in field:
                    mapping['timestamp'] = fieldnames[i]
                    break
            if 'timestamp' in mapping:
                break
        
        # Sender columns
        sender_candidates = ['sender', 'from', 'author', 'user', 'name', 'username']
        for candidate in sender_candidates:
            for i, field in enumerate(fieldnames_lower):
                if candidate in field:
                    mapping['sender'] = fieldnames[i]
                    break
            if 'sender' in mapping:
                break
        
        # Content columns
        content_candidates = ['content', 'message', 'text', 'body', 'msg']
        for candidate in content_candidates:
            for i, field in enumerate(fieldnames_lower):
                if candidate in field:
                    mapping['content'] = fieldnames[i]
                    break
            if 'content' in mapping:
                break
        
        return mapping
    
    def _parse_flexible_timestamp(self, timestamp_str: str) -> datetime:
        """Parse timestamp with multiple format attempts"""
        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S.%fZ",
            "%m/%d/%Y %H:%M:%S",
            "%m/%d/%y %H:%M:%S",
            "%d/%m/%Y %H:%M:%S",
            "%d/%m/%y %H:%M:%S",
            "%Y-%m-%d",
            "%m/%d/%Y",
            "%d/%m/%Y",
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(timestamp_str, fmt)
            except ValueError:
                continue
        
        # Try parsing as timestamp
        try:
            return datetime.fromtimestamp(float(timestamp_str))
        except:
            pass
        
        # Fallback
        return datetime.now(timezone.utc)
    
    async def _process_json(self, data: Union[str, Dict], mode: ProcessingMode) -> Tuple[List[ProcessedMessage], Dict, List[str], List[str]]:
        """Process generic JSON format"""
        messages = []
        errors = []
        warnings = []
        
        try:
            if isinstance(data, str):
                data = json.loads(data)
            
            # Try to find message-like structures
            message_candidates = self._find_message_structures(data)
            
            for i, msg_data in enumerate(message_candidates):
                try:
                    processed_msg = ProcessedMessage(
                        id=f"json_{i}",
                        sender=self._extract_field(msg_data, ['sender', 'from', 'author', 'user', 'name']),
                        content=self._extract_field(msg_data, ['content', 'message', 'text', 'body']),
                        timestamp=self._extract_timestamp(msg_data),
                        platform="json",
                        metadata={"original_data": msg_data}
                    )
                    
                    messages.append(processed_msg)
                    
                except Exception as e:
                    errors.append(f"Error processing JSON message {i}: {e}")
            
            metadata = {
                "platform": "json",
                "structure_type": "generic",
                "total_candidates": len(message_candidates)
            }
            
        except Exception as e:
            errors.append(f"Error parsing JSON data: {e}")
            metadata = {"platform": "json", "error": str(e)}
        
        return messages, metadata, errors, warnings
    
    def _find_message_structures(self, data: Union[Dict, List]) -> List[Dict]:
        """Find message-like structures in JSON data"""
        candidates = []
        
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    candidates.append(item)
        elif isinstance(data, dict):
            # Check if this is a single message
            if any(key in data for key in ['content', 'message', 'text', 'body']):
                candidates.append(data)
            else:
                # Look for nested message arrays
                for key, value in data.items():
                    if isinstance(value, list):
                        candidates.extend(self._find_message_structures(value))
                    elif isinstance(value, dict):
                        candidates.extend(self._find_message_structures(value))
        
        return candidates
    
    def _extract_field(self, data: Dict, field_names: List[str]) -> str:
        """Extract field value from data using multiple possible field names"""
        for field_name in field_names:
            if field_name in data:
                value = data[field_name]
                return str(value) if value is not None else ''
        return 'Unknown'
    
    def _extract_timestamp(self, data: Dict) -> datetime:
        """Extract timestamp from message data"""
        timestamp_fields = ['timestamp', 'date', 'time', 'created_at', 'sent_at', 'ts']
        
        for field in timestamp_fields:
            if field in data:
                timestamp_value = data[field]
                
                if isinstance(timestamp_value, (int, float)):
                    # Unix timestamp
                    try:
                        if timestamp_value > 1e10:  # Milliseconds
                            return datetime.fromtimestamp(timestamp_value / 1000)
                        else:  # Seconds
                            return datetime.fromtimestamp(timestamp_value)
                    except:
                        pass
                elif isinstance(timestamp_value, str):
                    # String timestamp
                    return self._parse_flexible_timestamp(timestamp_value)
        
        return datetime.now(timezone.utc)
    
    async def _process_text(self, data: str, mode: ProcessingMode) -> Tuple[List[ProcessedMessage], Dict, List[str], List[str]]:
        """Process plain text transcript"""
        messages = []
        errors = []
        warnings = []
        
        # Common transcript patterns
        patterns = [
            r'^(\w+): (.+)$',  # Speaker: message
            r'^\[(\d{2}:\d{2})\] (\w+): (.+)$',  # [HH:MM] Speaker: message
            r'^(\d{1,2}:\d{2} [AP]M) (\w+): (.+)$',  # HH:MM AM/PM Speaker: message
            r'^(\w+) says: (.+)$',  # Speaker says: message
        ]
        
        lines = data.split('\n')
        current_speaker = None
        current_content = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            matched = False
            for pattern in patterns:
                match = re.match(pattern, line)
                if match:
                    # Save previous message if exists
                    if current_speaker and current_content:
                        processed_msg = ProcessedMessage(
                            id=f"text_{len(messages)}",
                            sender=current_speaker,
                            content='\n'.join(current_content),
                            timestamp=datetime.now(timezone.utc),
                            platform="text",
                            metadata={"line_range": f"{i-len(current_content)}-{i-1}"}
                        )
                        messages.append(processed_msg)
                    
                    # Start new message
                    groups = match.groups()
                    if len(groups) == 2:  # Speaker: message
                        current_speaker = groups[0]
                        current_content = [groups[1]]
                    elif len(groups) == 3:  # [time] Speaker: message or time Speaker: message
                        current_speaker = groups[1]
                        current_content = [groups[2]]
                    
                    matched = True
                    break
            
            if not matched:
                # Continuation of current message
                if current_content:
                    current_content.append(line)
                else:
                    # Standalone line, treat as unknown speaker
                    processed_msg = ProcessedMessage(
                        id=f"text_{len(messages)}",
                        sender="Unknown",
                        content=line,
                        timestamp=datetime.now(timezone.utc),
                        platform="text",
                        metadata={"line_number": i}
                    )
                    messages.append(processed_msg)
        
        # Save final message if exists
        if current_speaker and current_content:
            processed_msg = ProcessedMessage(
                id=f"text_{len(messages)}",
                sender=current_speaker,
                content='\n'.join(current_content),
                timestamp=datetime.now(timezone.utc),
                platform="text",
                metadata={"line_range": f"{len(lines)-len(current_content)}-{len(lines)-1}"}
            )
            messages.append(processed_msg)
        
        metadata = {
            "platform": "text",
            "format": "transcript",
            "total_lines": len(lines),
            "processed_messages": len(messages)
        }
        
        return messages, metadata, errors, warnings
    
    async def _process_audio(self, data: bytes, mode: ProcessingMode) -> Tuple[List[ProcessedMessage], Dict, List[str], List[str]]:
        """Process audio file using speech recognition"""
        messages = []
        errors = []
        warnings = []
        
        if not SPEECH_RECOGNITION_AVAILABLE:
            errors.append("Speech recognition not available. Install speech_recognition library.")
            return messages, {"platform": "audio", "error": "Speech recognition unavailable"}, errors, warnings
        
        try:
            # Save audio data to temporary file
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file.write(data)
                temp_file_path = temp_file.name
            
            # Initialize recognizer
            r = sr.Recognizer()
            
            # Load audio file
            with sr.AudioFile(temp_file_path) as source:
                audio = r.record(source)
            
            # Perform speech recognition
            try:
                text = r.recognize_google(audio)
                
                processed_msg = ProcessedMessage(
                    id="audio_transcript",
                    sender="Audio Speaker",
                    content=text,
                    timestamp=datetime.now(timezone.utc),
                    platform="audio",
                    metadata={
                        "recognition_engine": "google",
                        "confidence": "unknown"
                    }
                )
                
                messages.append(processed_msg)
                
            except sr.UnknownValueError:
                warnings.append("Could not understand audio")
            except sr.RequestError as e:
                errors.append(f"Speech recognition service error: {e}")
            
            # Clean up temporary file
            os.unlink(temp_file_path)
            
            metadata = {
                "platform": "audio",
                "processing_method": "speech_recognition",
                "file_size_bytes": len(data)
            }
            
        except Exception as e:
            errors.append(f"Error processing audio: {e}")
            metadata = {"platform": "audio", "error": str(e)}
        
        return messages, metadata, errors, warnings
    
    async def _process_image(self, data: bytes, mode: ProcessingMode) -> Tuple[List[ProcessedMessage], Dict, List[str], List[str]]:
        """Process image using OCR"""
        messages = []
        errors = []
        warnings = []
        
        if not OCR_AVAILABLE:
            errors.append("OCR not available. Install PIL and pytesseract.")
            return messages, {"platform": "image", "error": "OCR unavailable"}, errors, warnings
        
        try:
            # Load image
            image = Image.open(io.BytesIO(data))
            
            # Perform OCR
            text = pytesseract.image_to_string(image)
            
            if text.strip():
                processed_msg = ProcessedMessage(
                    id="image_ocr",
                    sender="Image Text",
                    content=text.strip(),
                    timestamp=datetime.now(timezone.utc),
                    platform="image",
                    metadata={
                        "extraction_method": "ocr",
                        "image_size": image.size,
                        "image_mode": image.mode
                    }
                )
                
                messages.append(processed_msg)
            else:
                warnings.append("No text found in image")
            
            metadata = {
                "platform": "image",
                "processing_method": "ocr",
                "image_size": image.size,
                "file_size_bytes": len(data)
            }
            
        except Exception as e:
            errors.append(f"Error processing image: {e}")
            metadata = {"platform": "image", "error": str(e)}
        
        return messages, metadata, errors, warnings
    
    async def _process_pdf(self, data: Union[str, bytes], mode: ProcessingMode) -> Tuple[List[ProcessedMessage], Dict, List[str], List[str]]:
        """Process PDF document"""
        messages = []
        errors = []
        warnings = []
        
        try:
            import PyPDF2
            
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            # Read PDF
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(data))
            
            full_text = ""
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    full_text += page_text + "\n"
                except Exception as e:
                    warnings.append(f"Error extracting text from page {page_num + 1}: {e}")
            
            if full_text.strip():
                # Try to parse as conversation if it looks like one
                text_messages, text_metadata, text_errors, text_warnings = await self._process_text(full_text, mode)
                
                if text_messages:
                    # Update platform info
                    for msg in text_messages:
                        msg.platform = "pdf"
                        msg.metadata["source"] = "pdf_extraction"
                    messages.extend(text_messages)
                    errors.extend(text_errors)
                    warnings.extend(text_warnings)
                else:
                    # Treat as single document
                    processed_msg = ProcessedMessage(
                        id="pdf_content",
                        sender="PDF Document",
                        content=full_text.strip(),
                        timestamp=datetime.now(timezone.utc),
                        platform="pdf",
                        metadata={
                            "extraction_method": "pypdf2",
                            "page_count": len(pdf_reader.pages)
                        }
                    )
                    messages.append(processed_msg)
            else:
                warnings.append("No text found in PDF")
            
            metadata = {
                "platform": "pdf",
                "processing_method": "pypdf2",
                "page_count": len(pdf_reader.pages),
                "file_size_bytes": len(data)
            }
            
        except ImportError:
            errors.append("PDF processing not available. Install PyPDF2.")
            metadata = {"platform": "pdf", "error": "PyPDF2 unavailable"}
        except Exception as e:
            errors.append(f"Error processing PDF: {e}")
            metadata = {"platform": "pdf", "error": str(e)}
        
        return messages, metadata, errors, warnings
    
    async def process_real_time_stream(self, message_data: Dict[str, Any]) -> ProcessedMessage:
        """Process real-time message stream"""
        try:
            processed_msg = ProcessedMessage(
                id=message_data.get('id', f"realtime_{datetime.now(timezone.utc).timestamp()}"),
                sender=message_data.get('sender', 'Unknown'),
                content=message_data.get('content', ''),
                timestamp=datetime.fromisoformat(message_data.get('timestamp', datetime.now(timezone.utc).isoformat())),
                platform=message_data.get('platform', 'realtime'),
                message_type=message_data.get('type', 'text'),
                metadata=message_data.get('metadata', {})
            )
            
            return processed_msg
            
        except Exception as e:
            logger.error(f"Error processing real-time message: {e}")
            # Return a basic message with error info
            return ProcessedMessage(
                id=f"error_{datetime.now(timezone.utc).timestamp()}",
                sender="System",
                content=f"Error processing message: {e}",
                timestamp=datetime.now(timezone.utc),
                platform="error",
                metadata={"error": str(e)}
            )
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported input formats"""
        return [format_type.value for format_type in InputFormat]
    
    def get_processing_modes(self) -> List[str]:
        """Get list of supported processing modes"""
        return [mode.value for mode in ProcessingMode]
    
    async def validate_input(self, input_data: Union[str, bytes, Dict[str, Any]], 
                           max_size_mb: float = 50.0) -> Tuple[bool, List[str]]:
        """Validate input data before processing"""
        errors = []
        
        # Check size
        if isinstance(input_data, (str, bytes)):
            size_mb = len(input_data) / (1024 * 1024)
            if size_mb > max_size_mb:
                errors.append(f"Input size ({size_mb:.2f} MB) exceeds maximum ({max_size_mb} MB)")
        
        # Check if data is empty
        if not input_data:
            errors.append("Input data is empty")
        
        return len(errors) == 0, errors
    
    def to_dict(self, result: ProcessingResult) -> Dict[str, Any]:
        """Convert ProcessingResult to dictionary for JSON serialization"""
        return {
            "messages": [asdict(msg) for msg in result.messages],
            "metadata": result.metadata,
            "format_detected": result.format_detected.value,
            "processing_stats": result.processing_stats,
            "errors": result.errors,
            "warnings": result.warnings,
            "confidence_score": result.confidence_score,
            "participants": result.participants,
            "date_range": [result.date_range[0].isoformat(), result.date_range[1].isoformat()],
            "total_messages": result.total_messages,
            "processing_time": result.processing_time
        }


# Utility functions for external use
async def process_conversation_data(input_data: Union[str, bytes, Dict[str, Any]], 
                                  filename: Optional[str] = None,
                                  format_hint: Optional[str] = None,
                                  processing_mode: str = "batch") -> Dict[str, Any]:
    """Convenience function for processing conversation data"""
    processor = MultiFormatProcessor()
    
    # Convert string format hint to enum
    format_enum = None
    if format_hint:
        try:
            format_enum = InputFormat(format_hint)
        except ValueError:
            pass
    
    # Convert string processing mode to enum
    try:
        mode_enum = ProcessingMode(processing_mode)
    except ValueError:
        mode_enum = ProcessingMode.BATCH
    
    result = await processor.process_input(
        input_data=input_data,
        filename=filename,
        format_hint=format_enum,
        processing_mode=mode_enum
    )
    
    return processor.to_dict(result)


def get_format_info() -> Dict[str, Any]:
    """Get information about supported formats and their capabilities"""
    return {
        "supported_formats": {
            InputFormat.WHATSAPP_EXPORT: {
                "name": "WhatsApp Export",
                "description": "WhatsApp chat export in text format",
                "file_extensions": [".txt"],
                "features": ["timestamps", "participants", "message_content"]
            },
            InputFormat.MESSENGER_JSON: {
                "name": "Facebook Messenger",
                "description": "Facebook Messenger JSON export",
                "file_extensions": [".json"],
                "features": ["timestamps", "participants", "message_content", "reactions", "media"]
            },
            InputFormat.DISCORD_JSON: {
                "name": "Discord Export",
                "description": "Discord chat export in JSON format",
                "file_extensions": [".json"],
                "features": ["timestamps", "participants", "message_content", "attachments", "embeds"]
            },
            InputFormat.SLACK_JSON: {
                "name": "Slack Export",
                "description": "Slack conversation export in JSON format",
                "file_extensions": [".json"],
                "features": ["timestamps", "participants", "message_content", "threads", "files"]
            },
            InputFormat.TEAMS_EXPORT: {
                "name": "Microsoft Teams",
                "description": "Microsoft Teams chat export",
                "file_extensions": [".txt"],
                "features": ["timestamps", "participants", "message_content"]
            },
            InputFormat.TELEGRAM_JSON: {
                "name": "Telegram Export",
                "description": "Telegram chat export in JSON format",
                "file_extensions": [".json"],
                "features": ["timestamps", "participants", "message_content", "media", "forwarding"]
            },
            InputFormat.SMS_BACKUP: {
                "name": "SMS Backup",
                "description": "SMS backup in XML format",
                "file_extensions": [".xml"],
                "features": ["timestamps", "participants", "message_content", "read_status"]
            },
            InputFormat.EMAIL_MBOX: {
                "name": "Email MBOX",
                "description": "Email messages in MBOX format",
                "file_extensions": [".mbox"],
                "features": ["timestamps", "participants", "message_content", "subjects", "headers"]
            },
            InputFormat.CSV_GENERIC: {
                "name": "Generic CSV",
                "description": "Conversation data in CSV format",
                "file_extensions": [".csv"],
                "features": ["flexible_columns", "timestamps", "participants", "message_content"]
            },
            InputFormat.JSON_GENERIC: {
                "name": "Generic JSON",
                "description": "Conversation data in generic JSON format",
                "file_extensions": [".json"],
                "features": ["flexible_structure", "timestamps", "participants", "message_content"]
            },
            InputFormat.TEXT_TRANSCRIPT: {
                "name": "Text Transcript",
                "description": "Plain text conversation transcript",
                "file_extensions": [".txt"],
                "features": ["participants", "message_content", "flexible_format"]
            },
            InputFormat.AUDIO_FILE: {
                "name": "Audio File",
                "description": "Audio file with speech recognition",
                "file_extensions": [".wav", ".mp3", ".m4a"],
                "features": ["speech_recognition", "transcription"],
                "requirements": ["speech_recognition library"]
            },
            InputFormat.IMAGE_SCREENSHOT: {
                "name": "Image Screenshot",
                "description": "Image with text extraction via OCR",
                "file_extensions": [".png", ".jpg", ".jpeg"],
                "features": ["ocr", "text_extraction"],
                "requirements": ["PIL", "pytesseract"]
            },
            InputFormat.PDF_DOCUMENT: {
                "name": "PDF Document",
                "description": "PDF document with text extraction",
                "file_extensions": [".pdf"],
                "features": ["text_extraction", "multi_page"],
                "requirements": ["PyPDF2"]
            },
            InputFormat.REAL_TIME_STREAM: {
                "name": "Real-time Stream",
                "description": "Real-time message stream processing",
                "file_extensions": [],
                "features": ["real_time", "streaming", "live_processing"]
            }
        },
        "processing_modes": {
            ProcessingMode.BATCH: {
                "name": "Batch Processing",
                "description": "Process all data at once",
                "use_cases": ["file_uploads", "historical_data", "complete_conversations"]
            },
            ProcessingMode.STREAMING: {
                "name": "Streaming Processing",
                "description": "Process data in chunks as it arrives",
                "use_cases": ["large_files", "memory_optimization", "progressive_loading"]
            },
            ProcessingMode.REAL_TIME: {
                "name": "Real-time Processing",
                "description": "Process messages as they are received",
                "use_cases": ["live_conversations", "instant_analysis", "real_time_coaching"]
            },
            ProcessingMode.INCREMENTAL: {
                "name": "Incremental Processing",
                "description": "Process only new/changed data",
                "use_cases": ["updates", "sync_operations", "delta_processing"]
            }
        },
        "capabilities": {
            "max_file_size_mb": 50,
            "supported_encodings": ["utf-8", "latin-1", "ascii"],
            "concurrent_processing": True,
            "format_auto_detection": True,
            "error_recovery": True,
            "metadata_extraction": True,
            "participant_identification": True,
            "timestamp_parsing": True
        }
    }


if __name__ == "__main__":
    # Example usage
    import asyncio
    
    async def test_processor():
        processor = MultiFormatProcessor()
        
        # Test with sample WhatsApp data
        sample_whatsapp = """
12/25/23, 10:30 AM - Alice: Hey, how are you doing?
12/25/23, 10:31 AM - Bob: I'm good! How about you?
12/25/23, 10:32 AM - Alice: Great! Want to meet up later?
12/25/23, 10:33 AM - Bob: Sure, what time works for you?
        """.strip()
        
        result = await processor.process_input(sample_whatsapp)
        print(f"Processed {len(result.messages)} messages")
        print(f"Detected format: {result.format_detected}")
        print(f"Participants: {result.participants}")
        
        for msg in result.messages[:2]:  # Show first 2 messages
            print(f"{msg.timestamp} - {msg.sender}: {msg.content}")
    
    # Run test
    # asyncio.run(test_processor())