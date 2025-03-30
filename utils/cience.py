import asyncio
import re
from html import unescape

import requests
from crawl4ai import AsyncWebCrawler
from langchain_openai import ChatOpenAI

from core.config import settings
from schemas.company import CompanyList, CompanyWithLinkedinSlug

model = ChatOpenAI(api_key=settings.OPENAI_API_KEY, model="gpt-4o", temperature=0)


def get_cience_pages(industry_group: str, revenue: str, max_pages: int = None) -> list[str]:
    """
    Fetch the list of pages from Cience database for the given industry group and revenue.

    Args:
        industry_group: The industry group to fetch pages for.
        revenue: The revenue threshold to fetch pages for.
        max_pages: The maximum number of pages to fetch, defaults to None.

    Returns:
        A list of URLs of the pages from Cience database.
    """
    pages = []

    page = 1
    while True:
        url = f"https://www.cience.com/companies-database/united-states/{industry_group}/revenue-{revenue}?page={page}"
        res = requests.get(url)
        if "404 Not Found" not in res.text:
            pages.append(url)
            page += 1
            if max_pages and page > max_pages:
                print("Found", len(pages), "pages for", industry_group, "companies with revenue", revenue)
                break
        else:
            print("Found", len(pages), "pages for", industry_group, "companies with revenue", revenue)
            break

    return pages


async def get_cience_page_contents(pages: list[str]) -> list[str]:
    """
    Fetch the content of a list of pages from the Cience database as markdown.

    Args:
        pages: A list of URLs of the pages to fetch.

    Returns:
        A list of markdown content of the pages.
    """
    contents: list[str] = []

    # Use the AsyncWebCrawler to fetch the pages in parallel
    async with AsyncWebCrawler() as crawler:
        results = await crawler.arun_many(pages)

        # Extract the HTML content from each page
        for result in results:
            contents.append(result.markdown)

    return contents


structured_llm = model.with_structured_output(CompanyList)
input_prompt = """
Content: ```{page_content}```

The content below has been scraped from a website which contains information about various companies. Treat it as raw text.
Extract the details for all companies mentioned and return the output as a JSON list with the following fields:
- Company Name
- Industry
- Location
- Revenue
- Number of Employees
- URL to the company details page

Do **not** include CIENCE.
Return only a JSON list of objects, with no additional text.
"""


def get_linkedin_slug(company_details_page_url: str) -> str:
    """
    Extract the LinkedIn company slug from the content of the company details page.

    Args:
        company_details_page_url: The URL to the company details page on cience.

    Returns:
        The LinkedIn company slug.
    """

    # Fetch the company details page
    company_details_page = requests.get(company_details_page_url)

    # Use a regular expression to search for the LinkedIn company slug in the page content
    matches = re.search(r"https://linkedin.com/company/([^/'\"]+)", company_details_page.text)

    # If the slug was not found, return an empty string
    if matches is None:
        return ""

    # If the slug was found, return it
    return unescape(matches.group(1))


def get_companies_from_page_content(page_content: str) -> list[CompanyWithLinkedinSlug]:
    """
    Extract companies from the markdown content of a page as a list of CompanyWithLinkedinSlug objects.

    Args:
        page_content: The markdown content of the page as a string.

    Returns:
        A list of CompanyWithLinkedinSlug objects.
    """
    response = structured_llm.invoke(input_prompt.format(page_content=page_content))

    companies = []
    for company in response.model_dump()["companies"]:
        companies.append(
            CompanyWithLinkedinSlug(**company, linkedin_slug=get_linkedin_slug(company["cience_details_page"]))
        )

    return companies


def get_companies(industry_group: str, revenue: str, max_pages: int = None) -> list[CompanyWithLinkedinSlug]:
    """
    Fetch the list of companies from the Cience database for the given industry group and revenue.

    Args:
        industry_group: The industry group to fetch companies for.
        revenue: The revenue threshold to fetch companies for.
        max_pages: The maximum number of search result pages to check, defaults to going through all pages.

    Returns:
        A list of CompanyWithLinkedinSlug objects.
    """
    # Fetch the list of pages from Cience database
    pages = get_cience_pages(industry_group, revenue, max_pages)

    # Fetch the content of the pages as markdown
    contents = asyncio.run(get_cience_page_contents(pages))

    companies = []
    for i, page_content in enumerate(contents):
        # Extract companies from each page content
        print("\nParsing page", i + 1, "of", len(contents))
        companies_from_content = get_companies_from_page_content(page_content)
        companies.extend(companies_from_content)
        print("Extracted", len(companies_from_content), "companies from page", i + 1, "of", len(contents))

    return companies


if __name__ == "__main__":
    # industry_group = "internet"
    # revenue = "over-1b"
    #
    # companies = get_companies(industry_group, revenue, 1)
    # print(companies)

    print(get_linkedin_slug("https://www.cience.com/company/tony-betten-ford-sons/1149267264597656622"))
