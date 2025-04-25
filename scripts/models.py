from pydantic import BaseModel, Field, HttpUrl

class InputRow(BaseModel):
	"""Schema for the input CSV rows."""

	siteName: str = Field(..., min_length=1)
	siteURL: HttpUrl
	username: str = Field(..., min_length=1)
	password: str = Field(..., min_length=1)
	navHelper: str = Field(..., min_length=1)


class OutputRow(BaseModel):
	"""Schema for the output CSV rows."""

	siteName: str
	siteURL: HttpUrl
	status: str

	model_config = {"csv_headers": ["siteName", "siteURL", "status"]}


# class ExtractResult(BaseModel):
# 	billing_date: str = Field(description="The date of the invoice (MM/DD/YYY), or the invoice period")
# 	currency: str = Field(default="GBP", description="The currency of the invoice e.g. GBP or USD.")
# 	amount: float = Field(description="The invoice amount before tax. If not available use the total invoice amount")
# 	amount_including_tax: float = Field(description="The invoice amount including tax. If not available use the total invoice amount")