"""
NexusFlow Backend — FastAPI + LangChain AI Triage Engine
Author: Senior Full-Stack AI Engineer
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import json
import os
import random
from datetime import datetime, timedelta
import uuid
from dotenv import load_dotenv
import imaplib
import email
from email.header import decode_header

# Load .env file if present
load_dotenv()

# LangChain & LLM imports
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI

# ──────────────────────────────────────────────
# App Setup
# ──────────────────────────────────────────────
app = FastAPI(
    title="NexusFlow API",
    description="Unified Communication Triage System — AI-Powered Priority Inbox",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ──────────────────────────────────────────────
# Pydantic Models
# ──────────────────────────────────────────────
class RawMessage(BaseModel):
    id: str
    source: str          # "gmail" | "slack"
    sender: str
    sender_role: str     # "manager" | "professor" | "colleague" | "newsletter" | etc.
    subject: str
    body: str
    timestamp: str
    channel: Optional[str] = None  # for Slack

class ProcessedMessage(BaseModel):
    id: str
    source: str
    sender: str
    sender_role: str
    subject: str
    body: str
    timestamp: str
    channel: Optional[str] = None
    category: str        # "Urgent/Action Required" | "Informational" | "Ignore/Newsletter"
    urgency_score: int   # 1–10
    tldr: str
    tags: List[str]
    processed_at: str

class TriageResponse(BaseModel):
    messages: List[ProcessedMessage]
    stats: dict
    processed_at: str

# ──────────────────────────────────────────────
# In-Memory JSON Store (Vector-ready stub)
# ──────────────────────────────────────────────
STORE_FILE = "message_store.json"

def load_store() -> List[dict]:
    if os.path.exists(STORE_FILE):
        with open(STORE_FILE, "r") as f:
            return json.load(f)
    return []

def save_store(data: List[dict]):
    with open(STORE_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ──────────────────────────────────────────────
# EMAIL FETCHER — REAL GMAIL via IMAP
# ──────────────────────────────────────────────
def fetch_real_gmails() -> List[RawMessage]:
    """Fetches real unread emails using IMAP."""
    email_user = os.getenv("GMAIL_ADDRESS")
    email_pass = os.getenv("GMAIL_APP_PASSWORD")
    
    if not email_user or not email_pass:
        print("[Demo Mode] No real Gmail credentials found. Using mock Gmail data.")
        return mock_gmail()

    messages = []
    try:
        print(f"Connecting to Gmail for {email_user}...")
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(email_user, email_pass)
        mail.select("inbox")
        
        # Search for recent emails (last 5 to keep the demo quick)
        status, messages_response = mail.search(None, "ALL")
        email_ids = messages_response[0].split()
        latest_ids = email_ids[-8:] if len(email_ids) > 8 else email_ids
        
        for e_id in reversed(latest_ids):
            status, msg_data = mail.fetch(e_id, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    
                    # Decode Subject
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else "utf-8", errors="ignore")
                        
                    sender = msg.get("From", "Unknown")
                    timestamp = datetime.utcnow().isoformat()
                    
                    # Decode Body
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                body = part.get_payload(decode=True).decode(errors="ignore")
                                break
                    else:
                        body = msg.get_payload(decode=True).decode(errors="ignore")
                        
                    messages.append(RawMessage(
                        id=str(uuid.uuid4()),
                        source="gmail",
                        sender=sender,
                        sender_role="external", # We don't know the role, let AI guess it
                        subject=str(subject),
                        body=body[:800], # Truncate super long emails
                        timestamp=timestamp
                    ))
                    
        mail.logout()
        return messages
    except Exception as e:
        print(f"[IMAP Error] {e}")
        return mock_gmail()


# ──────────────────────────────────────────────
# MOCK DATA — Fallback
# ──────────────────────────────────────────────
def mock_gmail() -> List[RawMessage]:
    now = datetime.utcnow()
    return [
        RawMessage(
            id=str(uuid.uuid4()),
            source="gmail",
            sender="Prof. Ananya Sharma",
            sender_role="professor",
            subject="URGENT: Final Project Submission Deadline Changed",
            body="Dear students, final project deadline is TOMORROW at 11:59 PM. Please ensure everything is uploaded.",
            timestamp=(now - timedelta(minutes=15)).isoformat(),
        ),
        RawMessage(
            id=str(uuid.uuid4()),
            source="gmail",
            sender="Rajan Mehta (Manager)",
            sender_role="manager",
            subject="Q2 Performance Review — Action Required",
            body="Hi team, please complete your self-assessment by EOD.",
            timestamp=(now - timedelta(hours=1)).isoformat(),
        )
    ]

def fetch_messages() -> List[RawMessage]:
    """Combines real Gmails (if configured) with mock Slack messages."""
    
    # Get Gmails
    gmails = fetch_real_gmails()
    
    # Keep Slack as Mock for Demo
    now = datetime.utcnow()
    mock_slack = [
        RawMessage(
            id=str(uuid.uuid4()),
            source="slack",
            sender="Sarah (CTO)",
            sender_role="manager",
            subject="Production server is DOWN",
            body="@channel ALERT: API returning 500. Users affected. Join the incident bridge immediately. P0.",
            timestamp=(now - timedelta(minutes=5)).isoformat(),
            channel="#incidents",
        ),
        RawMessage(
            id=str(uuid.uuid4()),
            source="slack",
            sender="Design Bot",
            sender_role="newsletter",
            subject="Figma digests",
            body="3 new comments on the prototype.",
            timestamp=(now - timedelta(hours=2)).isoformat(),
            channel="#design",
        )
    ]

    all_messages = gmails + mock_slack
    return all_messages


# ──────────────────────────────────────────────
# LLM AI Processor (LangChain + Gemini)
# ──────────────────────────────────────────────

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

TRIAGE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are NexusFlow's AI Triage Engine. Your job is to analyze communication messages
and categorize them for a busy professional. You must be strict and accurate.

PRIORITY RULES (apply these first before scoring):
- Messages from a "professor" or "manager" or "CTO" or authority figure → base score ≥ 7
- Messages containing words like "URGENT", "deadline", "action required", "P0", "production down" → score ≥ 8
- Newsletters, promotional emails, non-actionable digests → score ≤ 3, category = Ignore/Newsletter
- System alerts about billing, CI/CD failures → score 5-7 based on severity
- Social/casual messages from colleagues → score 3-5, Informational

CATEGORIES:
1. "Urgent/Action Required" → score 7-10
2. "Informational" → score 4-6  
3. "Ignore/Newsletter" → score 1-3

Return ONLY valid JSON with this exact structure:
{{
  "category": "Urgent/Action Required" | "Informational" | "Ignore/Newsletter",
  "urgency_score": <integer 1-10>,
  "tldr": "<one crisp sentence TL;DR, max 20 words>",
  "tags": ["<tag1>", "<tag2>", "<tag3>"]
}}"""),
    ("human", """Analyze this message:

Source: {source}
Sender: {sender}
Sender Role: {sender_role}
Subject: {subject}
Body: {body}

Return the JSON analysis.""")
])

def build_llm():
    """Initialize Gemini LLM via LangChain."""
    if not GEMINI_API_KEY:
        return None
    return ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=GEMINI_API_KEY,
        temperature=0.1,
    )

def rule_based_fallback(msg: RawMessage) -> dict:
    """
    Fast rule-based triage when LLM is unavailable.
    Used for demo reliability — no API key needed.
    """
    subject_lower = msg.subject.lower()
    body_lower = msg.body.lower()
    role = msg.sender_role.lower()

    urgent_keywords = ["urgent", "deadline", "action required", "p0", "production", 
                       "down", "failed", "critical", "immediately", "asap", "eod", "changed"]
    ignore_keywords = ["unsubscribe", "newsletter", "flash sale", "digest", "deals", "promo"]

    is_urgent_kw = any(kw in subject_lower or kw in body_lower for kw in urgent_keywords)
    is_ignore_kw = any(kw in subject_lower or kw in body_lower for kw in ignore_keywords)
    is_authority = role in ["manager", "professor", "cto", "authority"]
    is_newsletter = role == "newsletter"

    if is_newsletter or (is_ignore_kw and not is_authority):
        score = random.randint(1, 3)
        category = "Ignore/Newsletter"
        tldr = f"Promotional/newsletter content from {msg.sender}. Safe to ignore."
        tags = ["newsletter", "promotional", msg.source]
    elif is_authority or is_urgent_kw:
        score = random.randint(7, 10)
        category = "Urgent/Action Required"
        tldr = f"Urgent message from {msg.sender} requiring immediate attention."
        tags = ["urgent", role, msg.source]
    else:
        score = random.randint(4, 6)
        category = "Informational"
        tldr = f"General update from {msg.sender}. Review when available."
        tags = ["informational", role, msg.source]

    return {
        "category": category,
        "urgency_score": score,
        "tldr": tldr,
        "tags": tags,
    }

def process_message_with_ai(msg: RawMessage, llm=None) -> ProcessedMessage:
    """Process a single message: AI first, fallback to rules."""
    analysis = None

    if llm:
        try:
            chain = TRIAGE_PROMPT | llm | JsonOutputParser()
            analysis = chain.invoke({
                "source": msg.source,
                "sender": msg.sender,
                "sender_role": msg.sender_role,
                "subject": msg.subject,
                "body": msg.body,
            })
        except Exception as e:
            print(f"[AI Error] Falling back to rules: {e}")
            analysis = None

    if not analysis:
        analysis = rule_based_fallback(msg)

    return ProcessedMessage(
        **msg.dict(),
        category=analysis["category"],
        urgency_score=analysis["urgency_score"],
        tldr=analysis["tldr"],
        tags=analysis.get("tags", []),
        processed_at=datetime.utcnow().isoformat(),
    )

def compute_stats(messages: List[ProcessedMessage]) -> dict:
    urgent = [m for m in messages if m.category == "Urgent/Action Required"]
    info   = [m for m in messages if m.category == "Informational"]
    ignore = [m for m in messages if m.category == "Ignore/Newsletter"]
    gmail  = [m for m in messages if m.source == "gmail"]
    slack  = [m for m in messages if m.source == "slack"]

    return {
        "total": len(messages),
        "urgent_count": len(urgent),
        "informational_count": len(info),
        "ignore_count": len(ignore),
        "gmail_count": len(gmail),
        "slack_count": len(slack),
        "avg_urgency_score": round(
            sum(m.urgency_score for m in messages) / len(messages), 1
        ) if messages else 0,
    }


# ──────────────────────────────────────────────
# API Routes
# ──────────────────────────────────────────────

@app.get("/", tags=["Health"])
def root():
    return {
        "service": "NexusFlow API",
        "status": "operational",
        "version": "1.0.0",
        "docs": "/docs",
    }

@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.post("/api/triage", response_model=TriageResponse, tags=["Triage"])
def triage_messages():
    """
    Main endpoint: Fetch mock messages from Gmail/Slack,
    run AI triage, return prioritized inbox.
    """
    raw_messages = fetch_messages()
    llm = build_llm()

    processed = []
    for msg in raw_messages:
        result = process_message_with_ai(msg, llm)
        processed.append(result)

    # Sort: highest urgency first
    processed.sort(key=lambda m: m.urgency_score, reverse=True)

    # Persist to store
    store = [m.dict() for m in processed]
    save_store(store)

    return TriageResponse(
        messages=processed,
        stats=compute_stats(processed),
        processed_at=datetime.utcnow().isoformat(),
    )

@app.get("/api/messages", response_model=List[ProcessedMessage], tags=["Messages"])
def get_cached_messages(
    category: Optional[str] = None,
    source: Optional[str] = None,
    min_score: Optional[int] = None,
):
    """Return cached/stored processed messages with optional filters."""
    store = load_store()
    if not store:
        raise HTTPException(status_code=404, detail="No messages found. Run /api/triage first.")

    messages = [ProcessedMessage(**m) for m in store]

    if category:
        messages = [m for m in messages if m.category.lower() == category.lower()]
    if source:
        messages = [m for m in messages if m.source.lower() == source.lower()]
    if min_score is not None:
        messages = [m for m in messages if m.urgency_score >= min_score]

    return messages

@app.get("/api/stats", tags=["Stats"])
def get_stats():
    """Return inbox statistics from the latest triage run."""
    store = load_store()
    if not store:
        return {"message": "No data yet. Run /api/triage first."}
    messages = [ProcessedMessage(**m) for m in store]
    return compute_stats(messages)

@app.delete("/api/messages/clear", tags=["Messages"])
def clear_messages():
    """Clear all cached messages."""
    save_store([])
    return {"message": "Message store cleared."}

@app.get("/api/mock-data", tags=["Debug"])
def get_mock_data():
    """Preview raw mock messages without AI processing."""
    messages = fetch_messages()
    return [m.dict() for m in messages]
