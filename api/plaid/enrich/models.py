"""
Plaid Enrich Models

Pydantic models for transaction enrichment services.
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

class EnrichmentLocation(BaseModel):
    """Location information for enriched transactions"""
    address: Optional[str] = Field(None, description="Street address where transaction occurred")
    city: Optional[str] = Field(None, description="City where transaction occurred")
    region: Optional[str] = Field(None, description="Region or state where transaction occurred")
    postal_code: Optional[str] = Field(None, description="Postal code where transaction occurred")
    country: Optional[str] = Field(None, description="ISO 3166-1 alpha-2 country code")
    lat: Optional[float] = Field(None, description="Latitude where transaction occurred")
    lon: Optional[float] = Field(None, description="Longitude where transaction occurred")
    store_number: Optional[str] = Field(None, description="Merchant defined store number")

class CounterpartyAccountNumbers(BaseModel):
    """Account numbers associated with counterparty"""
    bacs: Optional[Dict[str, Optional[str]]] = Field(None, description="UK BACS account details")
    international: Optional[Dict[str, Optional[str]]] = Field(None, description="IBAN and BIC details")

class Counterparty(BaseModel):
    """Counterparty information extracted from transaction"""
    name: str = Field(..., description="Name of the counterparty (merchant, institution, etc.)")
    entity_id: Optional[str] = Field(None, description="Unique Plaid-generated ID for counterparty")
    type: str = Field(..., description="Type of counterparty (merchant, financial_institution, etc.)")
    website: Optional[str] = Field(None, description="Website associated with counterparty")
    logo_url: Optional[str] = Field(None, description="URL of 100x100 PNG logo")
    confidence_level: Optional[str] = Field(None, description="Confidence level (VERY_HIGH, HIGH, MEDIUM, LOW, UNKNOWN)")
    phone_number: Optional[str] = Field(None, description="Phone number in E.164 format")
    account_numbers: Optional[CounterpartyAccountNumbers] = Field(None, description="Account numbers when available")

class PersonalFinanceCategory(BaseModel):
    """Personal finance category information"""
    primary: str = Field(..., description="High level category")
    detailed: str = Field(..., description="Granular category conveying transaction intent")
    confidence_level: Optional[str] = Field(None, description="Confidence level for categorization")

class Recurrence(BaseModel):
    """Recurrence information for transactions"""
    is_recurring: Optional[bool] = Field(None, description="Whether transaction is periodically recurring")

class TransactionEnrichments(BaseModel):
    """Enrichment data for transactions"""
    counterparties: List[Counterparty] = Field([], description="Counterparties present in transaction")
    entity_id: Optional[str] = Field(None, description="Primary counterparty entity ID")
    legacy_category_id: Optional[str] = Field(None, description="Legacy category ID (deprecated)")
    legacy_category: Optional[List[str]] = Field(None, description="Legacy category hierarchy (deprecated)")
    location: Optional[EnrichmentLocation] = Field(None, description="Location where transaction took place")
    logo_url: Optional[str] = Field(None, description="URL of 100x100 PNG logo")
    merchant_name: Optional[str] = Field(None, description="Name of primary counterparty")
    payment_channel: str = Field(..., description="Payment channel: online, in store, other")
    phone_number: Optional[str] = Field(None, description="Phone number in E.164 format")
    personal_finance_category: Optional[PersonalFinanceCategory] = Field(None, description="Personal finance category")
    personal_finance_category_icon_url: Optional[str] = Field(None, description="Category icon URL")
    recurrence: Optional[Recurrence] = Field(None, description="Recurrence insights")
    website: Optional[str] = Field(None, description="Website associated with transaction")

class ClientProvidedTransaction(BaseModel):
    """Transaction data provided by client for enrichment"""
    id: str = Field(..., description="Unique ID for transaction")
    description: str = Field(..., description="Raw transaction description")
    amount: float = Field(..., description="Absolute value of transaction (>= 0)")
    direction: str = Field(..., description="Transaction direction: INFLOW or OUTFLOW")
    iso_currency_code: str = Field(..., description="ISO-4217 currency code")
    location: Optional[EnrichmentLocation] = Field(None, description="Optional location data")
    mcc: Optional[str] = Field(None, description="Merchant category code")
    date_posted: Optional[str] = Field(None, description="Date transaction posted (YYYY-MM-DD)")

class EnrichedTransaction(BaseModel):
    """Enriched transaction response"""
    id: str = Field(..., description="Unique transaction ID from request")
    description: str = Field(..., description="Raw transaction description")
    amount: float = Field(..., description="Absolute transaction value")
    direction: str = Field(..., description="Transaction direction: INFLOW or OUTFLOW")
    iso_currency_code: str = Field(..., description="ISO-4217 currency code")
    enrichments: TransactionEnrichments = Field(..., description="Plaid enrichment data")

class EnrichOptions(BaseModel):
    """Options for enrichment request"""
    include_legacy_category: bool = Field(False, description="Include legacy category in response")

class TransactionsEnrichRequest(BaseModel):
    """Request model for transaction enrichment"""
    account_type: str = Field(..., description="Account type: depository or credit")
    transactions: List[ClientProvidedTransaction] = Field(..., description="Transactions to enrich (max 100)")
    options: Optional[EnrichOptions] = Field(None, description="Optional enrichment settings")

class TransactionsEnrichResponse(BaseModel):
    """Response model for transaction enrichment"""
    enriched_transactions: List[EnrichedTransaction] = Field(..., description="List of enriched transactions")
    request_id: str = Field(..., description="Unique request identifier")