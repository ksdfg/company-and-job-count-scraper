from csv import DictWriter

import inquirer
from inquirer.errors import ValidationError

from utils.cience import CompanyWithLinkedinSlug, get_companies
from utils.linkedin import CompanyWithJobCounts, enrich_company_with_job_counts, setup_driver


def validate_numeric_input(_, choice) -> bool:
    """
    Validate if the provided choice is numeric or empty.

    Args:
        _: Unused argument, typically used for compatibility with inquirer prompt.
        choice: The user input to validate.

    Returns:
        bool: True if the choice is numeric or empty, raises ValidationError otherwise.

    Raises:
        ValidationError: If the input is not numeric or empty.
    """
    if choice.isnumeric() or choice == "":
        return True

    raise ValidationError(choice, "Input must be a number or empty")


def take_input():
    """
    Prompt the user for input regarding the industry group, revenue range, and the number of pages to search.

    Returns:
        tuple: A tuple containing the industry group, revenue range, and maximum number of pages to search.
    """
    # Ask for the industry group and format it appropriately
    industry_group = inquirer.text(message="What industry (from cience.com) do you want to search for?")
    industry_group = industry_group.lower().replace(" ", "-")
    print()

    # Ask for the revenue range from a predefined list of choices
    revenue = inquirer.list_input(
        message="What revenue range do you want to search for?",
        choices=[
            "under-1m",
            "1m-5m",
            "5m-10m",
            "10m-25m",
            "25m-50m",
            "50m-100m",
            "100m-250m",
            "250m-500m",
            "500m-1b",
            "over-1b",
        ],
    )
    print()

    # Ask for the maximum number of pages to search and validate the input
    max_pages = inquirer.text(
        message="How many result pages on cience do you want to search through? Leave empty to search through all pages",
        validate=validate_numeric_input,
    )
    print()

    # Convert max_pages to an integer if not empty, otherwise set it to None
    if max_pages:
        max_pages = int(max_pages)
    else:
        max_pages = None

    return industry_group, revenue, max_pages


def fetch_companies_from_cience(
    industry_group: str, revenue: str, max_pages: int = None
) -> list[CompanyWithLinkedinSlug]:
    """
    Fetch a list of companies from the Cience database for a given industry group and revenue range.

    Args:
        industry_group: The industry group to search within.
        revenue: The revenue range to filter companies.
        max_pages: The maximum number of result pages to fetch. Defaults to None for all pages.

    Returns:
        A list of CompanyWithLinkedinSlug objects representing the companies found.
    """
    # Print a header for the operation
    print("----------------------------------------------------")
    print("Fetching companies from cience.com")
    print("----------------------------------------------------")

    # Use the get_companies function to fetch companies based on the specified criteria
    companies = get_companies(industry_group, revenue, max_pages)

    # Display the number of companies found
    print("\nFound", len(companies), "companies", end="\n\n")

    return companies


def fetch_enriched_companies_from_linkedin(companies: list[CompanyWithLinkedinSlug]) -> list[CompanyWithJobCounts]:
    """
    Fetch job counts for a list of companies from LinkedIn.

    Args:
        companies: A list of CompanyWithLinkedinSlug objects to fetch job counts for.

    Returns:
        A list of CompanyWithJobCounts objects representing the companies with job counts.
    """
    print("----------------------------------------------------")
    print("Fetching job counts from linkedin")
    print("----------------------------------------------------")

    driver = setup_driver()
    print("Setup browser to search on linkedin", end="\n\n")

    enriched_companies = []
    for i, company in enumerate(companies):
        # If company has no LinkedIn slug, skip it
        if not company.linkedin_slug:
            print("Skipping", company.company_name, "because it has no linkedin slug")
            continue

        # Fetch job counts for the current company
        enriched_companies.append(enrich_company_with_job_counts(driver, company))
        print("Fetched job counts for", company.company_name, "(", i + 1, "/", len(companies), ")")

    # Clean up the driver
    driver.quit()
    print("\nFound", len(enriched_companies), "enriched companies", end="\n\n")

    return enriched_companies


def write_enriched_companies_to_file(enriched_companies: list[CompanyWithJobCounts]):
    """
    Write the list of enriched companies to a CSV file.

    Args:
        enriched_companies: A list of CompanyWithJobCounts objects to write to file.
    """
    print("----------------------------------------------------")
    print("Writing to file")
    print("----------------------------------------------------")

    # Open a file in write mode, and create a writer with the fieldnames from the first company
    with open(f"Companies_{industry_group}_{revenue}.csv", "w") as file:
        writer = DictWriter(file, fieldnames=enriched_companies[0].model_dump().keys())

        # Write the header with the fieldnames
        writer.writeheader()

        # Write each company to the file
        for company in enriched_companies:
            writer.writerow(company.model_dump())

    print(f"List written to Companies_{industry_group}_{revenue}.txt successfully")


if __name__ == "__main__":
    industry_group, revenue, max_pages = take_input()

    companies = fetch_companies_from_cience(industry_group, revenue, max_pages)

    enriched_companies = fetch_enriched_companies_from_linkedin(companies)

    if len(enriched_companies) > 0:
        write_enriched_companies_to_file(enriched_companies)
