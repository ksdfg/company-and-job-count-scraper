import json

import requests

from app.core.config import settings
from app.schemas.company import CompanyWithJobCounts, CompanyWithLinkedinSlug

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
    
    
    if response.status_code == 402:
        print("NOT ENOUGH CORESIGNAL CREDITS!")
        return -1

    # Get the number of job postings from the response headers
    job_count = response.headers.get("x-total-results")
    
    print(response.headers)
    print(f"Job count for {company_linkedin_slug} for {keyword_description}: {job_count}")
    print(f"Job IDs->{response.json()}")
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
    ai_jobs=search_jobs(company.linkedin_slug, "AI")
    engineer_jobs=search_jobs(company.linkedin_slug, "Engineer")
    it_jobs=search_jobs(company.linkedin_slug, "IT")
    
    return CompanyWithJobCounts(
        **company.model_dump(),
        ai_jobs=ai_jobs,
        engineer_jobs=engineer_jobs,
        it_jobs=it_jobs
    )


if __name__ == "__main__":
    company = CompanyWithLinkedinSlug(
        company_name="Faraday Future",
        industry="Automotive",
        location="United States, California",
        revenue="$1 Million to $5 Million",
        employees="1001-5000",
        cience_details_page="http://linkedin.com/company/faradayfuture",
        linkedin_slug="faradayfuture",
    )

    enriched_company = enrich_company_with_coresignal_job_counts(company)
