# Company and Job count scraper

This is a cli based tool that does the following

- It will scrape a list of companies from cience.com for a given industry group and revenue range
- It will then fetch the number of active jobs for each company with AI, Engineer and IT job titles
- It will then save the output to a csv file

## How to use

This requires `docker` to be installed. Please check
the [docker installation guide](https://docs.docker.com/get-docker/) to make sure you have it installed.

### Install

Run the following script from the repo root to build the docker image and set up the required tokens

```bash
sh ./scripts/install.sh
```

This will require you to enter your OpenAI and Coresignal API keys, which are required to run the scraper.

### Run

Run the following script from the repo root to launch the cli

```bash
sh ./scripts/run.sh
```

This will prompt you for the industry group and revenue range to scrape. After scraping, the results will be saved to a
csv file in the `./data` directory in the repo root.
