# Project requirements

## Purpose

- Provides a tool for the sales team to input search variables such as Vertical, Company size and Company revenue and
  keyword into the LinkedIn scrape tool, with variables

- Allow sales/BD teams to use the LI scrape tool to generate qualifying company prospect lists (XLS) with Open Reqs for
  AI, Engineering and IT position reqs.

## Points from engineer

### what have you built so far?

So far I have created a scraping tool which scrapes a website which has data for a lot of companies sorted by domain
and revenue (website provided by sales team). After getting the names of the companies, the tool goes to the job section
on the Linkedin page of each company and retrieves the number of job posting for “AI”, “Engineer” and “IT” by that
company and adds them to an excel sheet.

### what is the effort involved to build UI

The UI is to let the sales team select the domain and the revenue by which they want to scrape. Building the UI and
connecting it to the rest of the application will take a few days at least.

### Do you plan to make this a downloadable app that sales/DB folks can run from their laptop locally oy DO we need to host it?

It has to be a downloadable app that sales people can run on their laptops.

### If no of parameters expected are a few can we take them as command line parameters or read them from input file , Do we really need to build UI ??

Yes, we can use command line parameters, but I am not sure if sales will be able to run it. UI would make it easier
for them.

### Other blockers

Since LinkedIn has a strict policy against scraping and automation tools, they frequently ban accounts, in which case,
the cookie used to log in has to be changed. I think that might be a little too technical for the sales team to do by
themselves and may require frequent assistance from one of the engineers.