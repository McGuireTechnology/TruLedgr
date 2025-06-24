from sqlmodel import SQLModel, Field
from datetime import datetime
from pydantic import BaseModel


class WalmartReceiptLookupRequest(BaseModel):
    storeId: str = "888"  # Store ID for the Walmart Location
    purchaseDate: str = "04-28-2025"  # Format: MM-DD-YYYY
    cardType: str = "visa"  # Options: visa, mastercard, amex, discover
    total: str = "19.55"  # Total amount of the purchase
    lastFourDigits: str = "8898"  # Last four digits of the card used for the purchase


class WalmartReceiptLookup(SQLModel, table=True):
    __tablename__ = "walmart_receipt_lookups"
    id: int = Field(default=None, primary_key=True)
    storeId: str
    purchaseDate: str
    cardType: str
    total: str
    lastFourDigits: str
    result: str  # JSON string of the remote response
    result_status_code: int  # HTTP status code from the remote request
    requested_at: datetime = Field(default_factory=datetime.utcnow)


class WalmartStore(SQLModel, table=True):
    __tablename__ = "walmart_stores"
    store_id: str = Field(primary_key=True)
    addressLineOne: str
    addressLineTwo: str
    city: str
    postalCode: str
    country: str
    phoneNumber: str
    displayName: str


class WalmartReceipt(SQLModel, table=True):
    __tablename__ = "walmart_receipts"
    id: int = Field(default=None, primary_key=True)
    lookup_id: int = Field(foreign_key="walmart_receipt_lookups.id")
    store_id: str = Field(default=None, foreign_key="walmart_stores.store_id", nullable=True)
    dateTime: str
    noOfItems: int
    subtotal: float
    taxTotal: float
    totalAmount: float
    changeDue: float
    tcNumber: str
    barCodeImageUrl: str
    image: str  # base64 or URL


class WalmartReceiptItem(SQLModel, table=True):
    __tablename__ = "walmart_receipt_items"
    id: int = Field(default=None, primary_key=True)
    receipt_id: int = Field(foreign_key="walmart_receipts.id")
    description: str
    imageUrl: str
    itemId: str
    upc: str
    price: float
    quantity: int
