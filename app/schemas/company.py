from pydantic import BaseModel, Field


class Company(BaseModel):
    company_name: str = Field(description="The name of the company")
    industry: str = Field(description="The industry in which the company operates")
    location: str = Field(description="The location of the company's headquarters")
    revenue: str = Field(description="The company's annual revenue")
    employees: str = Field(description="The number of employees in the company")
    cience_details_page: str = Field(description="URL to the company details page")


class CompanyWithLinkedinSlug(Company):
    linkedin_slug: str = Field(description="The LinkedIn company slug")


class CompanyList(BaseModel):
    companies: list[Company] = Field(description="A list of companies")


class CompanyWithJobCounts(CompanyWithLinkedinSlug):
    ai_jobs: int = Field(description="The number of job postings for AI")
    engineer_jobs: int = Field(description="The number of job postings for Engineer")
    it_jobs: int = Field(description="The number of job postings for IT")
