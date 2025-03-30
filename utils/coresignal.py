import json

import requests

from core.config import settings
from schemas.company import CompanyWithJobCounts, CompanyWithLinkedinSlug

url = "https://api.coresignal.com/cdapi/v1/linkedin/job/search/filter"

headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Authorization": f"Bearer {settings.CORESIGNAL_API_KEY}",
}


def search_jobs(
    company_linkedin_slug: str,
    keyword_description: str,
) -> int:
    """
    Search for jobs on a given company on LinkedIn using the Coresignal API.

    Args:
        company_linkedin_slug: The LinkedIn company slug.
        keyword_description: The keyword description to search for.

    Returns:
        The number of job postings found.
    """
    payload = json.dumps(
        {
            "company_linkedin_url": f"https://www.linkedin.com/company/{company_linkedin_slug}",
            "keyword_description": keyword_description,
            "deleted": False,
            "application_active": True,
        }
    )
    response = requests.request("POST", url, headers=headers, data=payload)

    # Get the number of job postings from the response headers
    job_count = response.headers.get("x-total-results")
    # If the job count is not a number or is empty, return 0
    if not job_count or not job_count.isnumeric():
        return 0

    return int(job_count)


def enrich_company_with_coresignal_job_counts(
    company: CompanyWithLinkedinSlug,
) -> CompanyWithJobCounts:
    """
    Enrich a CompanyWithLinkedinSlug object with job counts for the company.

    The method takes a CompanyWithLinkedinSlug object and searches for job postings
    on LinkedIn for the given company and job titles "AI", "Engineer", and "IT".
    It extracts the number of job postings for each job title and returns a
    CompanyWithJobCounts object with the job counts.

    :param company: A CompanyWithLinkedinSlug object to enrich with job counts.
    :return: A CompanyWithJobCounts object with the job counts.
    """
    return CompanyWithJobCounts(
        **company.model_dump(),
        ai_jobs=search_jobs(company.linkedin_slug, "AI"),
        engineer_jobs=search_jobs(company.linkedin_slug, "Engineer"),
        it_jobs=search_jobs(company.linkedin_slug, "IT"),
    )


if __name__ == "__main__":
    company = CompanyWithLinkedinSlug(
        company_name="Opus",
        industry="Internet",
        location="United States, Illinois",
        revenue="$1B and Over",
        employees="11-50",
        cience_details_page="https://www.cience.com/company/opus/1639153433099655092",
        linkedin_slug="google",
    )

    enriched_company = enrich_company_with_coresignal_job_counts(company)
    print(enriched_company)
