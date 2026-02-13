# UK Vehicle Data Sources & APIs - Comprehensive Research

> Research compiled February 2026. Focus on what is actually available in 2025-2026 for UK vehicles.

---

## Table of Contents

1. [UK Government MOT History API](#1-uk-government-mot-history-api)
2. [DVLA Vehicle Enquiry Service (VES) API](#2-dvla-vehicle-enquiry-service-ves-api)
3. [Free/Public UK Vehicle Data Sources](#3-freepublic-uk-vehicle-data-sources)
4. [Commercial Vehicle Data Providers](#4-commercial-vehicle-data-providers)
5. [Market Pricing & Valuation Data Sources](#5-market-pricing--valuation-data-sources)
6. [Vehicle Identification / VIN Decoding](#6-vehicle-identification--vin-decoding)
7. [Insurance Write-Off Databases](#7-insurance-write-off-databases)
8. [Finance / Outstanding Finance Checks](#8-finance--outstanding-finance-checks)
9. [Stolen Vehicle Databases](#9-stolen-vehicle-databases)
10. [Recall Data](#10-recall-data)
11. [Emissions / ULEZ / Clean Air Zone Data](#11-emissions--ulez--clean-air-zone-data)
12. [Aggregator APIs (One-Stop-Shop Providers)](#12-aggregator-apis-one-stop-shop-providers)
13. [Summary: Recommended Architecture](#13-summary-recommended-architecture)

---

## 1. UK Government MOT History API

**Provider:** Driver and Vehicle Standards Agency (DVSA)
**URL:** https://documentation.history.mot.api.gov.uk/
**Cost:** FREE
**API:** Yes (REST/JSON)

### What Data It Provides

The MOT History API provides access to vehicle and MOT test information for vehicles registered in Great Britain and Northern Ireland.

**Vehicle record fields:**
- `registration` - Vehicle registration number
- `firstUsedDate` - Date vehicle was first registered
- `registrationDate` - Date vehicle was registered
- `manufactureDate` - Date vehicle was manufactured
- `primaryColour` / `secondaryColour` - Vehicle colours
- `engineSize` - Engine capacity
- `model` / `make` - Vehicle make and model
- `fuelType` - Fuel type
- `lastMotTestDate` - Date of last MOT test
- `dataSource` - Source (dvla, dvsa, or dva ni)
- `motTests` - Array of all MOT test results

**MOT test record fields (within `motTests` array):**
- `completedDate` - Date test was completed
- `motTestNumber` - Test certificate number
- `expiryDate` - Date the MOT expires
- `registrationAtTimeOfTest` - Registration at time of test
- `testResult` - PASSED or FAILED
- `odometerValue` - Odometer reading (KEY for mileage verification)
- `odometerUnit` - MI or KM
- `odometerResultType` - READ, UNREADABLE, or NO_ODOMETER
- `defects` - Array of defects found

**Defect record fields:**
- `dangerous` - Boolean indicating severity
- `text` - Description of the defect
- `type` - DANGEROUS, MAJOR, MINOR, ADVISORY, or PRS

### Coverage
- Cars, motorcycles, vans: GB since 2005, NI since 2017
- HGVs, trailers, buses, coaches: GB since 2018, NI since 2017

### Endpoints
- **Individual lookup:** By registration number or vehicle ID
- **Bulk download:** `/v1/trade/vehicles/bulk-download` - Download bulk + delta files (~500,000 records per file)

### Authentication
- Requires registration and API key approval from DVSA
- Each request needs: `Authorization: Bearer {access_token}` and `X-API-Key: {api_key}`
- Client secrets expire every 2 years

### Rate Limits
| Limit Type | Value |
|---|---|
| Daily Quota | 500,000 requests/day |
| Burst Limit | 10 requests in a short burst |
| Requests Per Second | 15 average RPS |
| Exceeded Penalty | 429 error; key blocked for 24 hours if daily quota exceeded |

### Important Notes
- As of September 1st 2025, the previous API version is **deprecated** - new version required
- The API is **free** to use
- Excellent for mileage history verification (odometer readings at each MOT)
- Advisory/failure data is invaluable for understanding vehicle condition

### Registration
https://documentation.history.mot.api.gov.uk/mot-history-api/register

---

## 2. DVLA Vehicle Enquiry Service (VES) API

**Provider:** Driver and Vehicle Licensing Agency (DVLA)
**URL:** https://developer-portal.driver-vehicle-licensing.api.gov.uk/
**Cost:** FREE tier available; paid tiers from ~2p per enquiry
**API:** Yes (REST/JSON)

### Endpoint
```
POST https://driver-vehicle-licensing.api.gov.uk/vehicle-enquiry/v1/vehicles
Test: POST https://uat.driver-vehicle-licensing.api.gov.uk/vehicle-enquiry/v1/vehicles
```

### Request
```json
{
  "registrationNumber": "TE57VRN"
}
```
VRN should exclude spaces and non-alphanumeric characters. VRN is passed in the body (not URL) as it is treated as sensitive data.

### Response Fields

| Field | Type | Example | Description |
|---|---|---|---|
| `registrationNumber` | string | WN67DSO | Registration number |
| `taxStatus` | enum | Taxed | Not Taxed for on Road Use, SORN, Taxed, Untaxed |
| `taxDueDate` | date | 2017-12-25 | Tax liability date |
| `artEndDate` | date | - | Additional Rate of Tax End Date |
| `motStatus` | enum | Valid | No details held, No results returned, Not valid, Valid |
| `motExpiryDate` | date | - | MOT expiration date |
| `make` | string | ROVER | Vehicle manufacturer |
| `monthOfFirstDvlaRegistration` | date | 2011-11 | DVLA registration month |
| `monthOfFirstRegistration` | date | 2012-12 | Initial registration month |
| `yearOfManufacture` | integer | 2004 | Manufacturing year |
| `engineCapacity` | integer | 1796 | Capacity in cc |
| `co2Emissions` | integer | 0 | Grams per kilometre |
| `fuelType` | string | PETROL | Method of propulsion |
| `markedForExport` | boolean | - | Export marking status |
| `colour` | string | Blue | Vehicle colour |
| `typeApproval` | string | N1 | Type approval category |
| `wheelplan` | string | NON STANDARD | Wheel configuration |
| `revenueWeight` | integer | 1640 | Weight in kg |
| `realDrivingEmissions` | string | 1 | RDE value |
| `dateOfLastV5CIssued` | date | - | V5C issue date |
| `euroStatus` | string | Euro 5 | Emissions standard (KEY for ULEZ) |
| `automatedVehicle` | boolean | - | Automated vehicle flag |

### Authentication
- Header: `x-api-key` with issued API key
- Only ONE API key permitted per customer/company

### Rate Limits
- Per-client limits based on subscription plan
- Overall service-wide limits to protect infrastructure
- 429 HTTP status returned when exceeded
- Exact limits depend on subscription tier

### Cost
- Free tier: Limited access
- Paid tiers: From approximately 2p per enquiry upwards, depending on data type and volume
- The DVLA bulk data set contains 47 different information fields

### Key Value for Car Check Service
- **Tax status** (is the car taxed/SORN?)
- **MOT status** (quick valid/invalid check)
- **Euro status** (for ULEZ/emissions compliance)
- **CO2 emissions** (for emissions/tax calculations)
- **Export status** (is car marked for export?)
- **V5C date** (ownership document date)
- **First registration date** (actual age verification)

---

## 3. Free/Public UK Vehicle Data Sources

### 3a. DVSA Open Data Portal
**URL:** https://open.data.dvsa.gov.uk/
**Cost:** FREE (Open Government Licence v3.0)
**API:** No - bulk download files

**Available datasets:**
1. **MOT Anonymised** - All MOT tests and outcomes since 2005/2022, including make, model, odometer reading, reasons for failure. ZIP files via AWS S3.
2. **MOT (operational metrics)** - MOT test outcomes and trends, vehicle safety and compliance data.
3. **Dangerous Goods (ADR)** - Driver training provider data.
4. **Vehicle Operator Licensing (VOL)** - Service satisfaction and completion rates.

**MOT Anonymised data includes:**
- Test results (2024 data added March 2025)
- Failure items with descriptions
- Historical data back to 2005
- User guides for pre/post May 2018 data structures
- Lookup tables for data interpretation

### 3b. Data.gov.uk Datasets
**URL:** https://www.data.gov.uk/
**Cost:** FREE

Key datasets:
- **Anonymised MOT tests and results** - https://www.data.gov.uk/dataset/c63fca52-ae4c-4b75-bab5-8b4735e1a4c9/anonymised-mot-tests-and-results
- **Vehicle licensing statistics data files** - https://www.gov.uk/government/statistical-data-sets/vehicle-licensing-statistics-data-files (updated quarterly, latest Jul-Sep 2025)
- **Vehicle Safety Branch Recalls Database** - https://www.data.gov.uk/dataset/18c00cf3-3bb2-4930-b30d-78113113aaa7/vehicle-safety-branch-recalls-database (NOTE: Last updated Feb 2016 - outdated)
- **GB Driving Licence Data** - Current driving licence statistics

### 3c. Find Transport Data (DfT)
**URL:** https://findtransportdata.dft.gov.uk/browse?selectedOrganisations=dvla
**Cost:** FREE

Lists all available datasets from DVLA, DVSA, and other transport bodies. A good starting point for discovering available government data.

### 3d. GOV.UK MOT Testing Statistics
**URL:** https://www.gov.uk/government/statistical-data-sets/mot-testing-data-for-great-britain
**Cost:** FREE

Statistical data on MOT testing rates, pass/fail rates by vehicle class, and trends.

### 3e. DVLA Bulk Data Access
**URL:** Contact DVLA directly
**Cost:** Paid (custom pricing)

Certain companies can request specialist vehicle data from DVLA including:
- 'Bulk data set' (47 fields per vehicle)
- 'Anonymised data set'
- Vehicle mileage data

Contact: dvlaapiaccess@dvla.gov.uk

---

## 4. Commercial Vehicle Data Providers

### 4a. CAP HPI (Cap hpi)
**URL:** https://www.cap-hpi.com/
**Type:** Enterprise/B2B
**Cost:** Custom pricing (contact sales)

**Products:**
- **hpi check** - The industry-standard vehicle history check
  - Vehicle Identity Check
  - Write-off Data (insurance write-off category)
  - Outstanding Finance
  - Stolen Vehicle Check (PNC data)
  - MOT Data
  - Safety Recall Data
  - Mileage discrepancy alerts
- **Black Book Live** - Real-time used vehicle valuations
- **Black Book +12** - 12-month valuation forecasts
- **Gold Book / Gold Book iQ** - Residual value forecasts
- **SPEC solution** - Vehicle specifications and technical data
- **cap Code** - Industry-standard vehicle identification coding system
- **Valuation Anywhere** - On-demand valuations for cars, bikes, LCVs, HGVs
- **SMR Data** - Service, Maintenance & Repair cost data
- **totalcost** - Lifetime running cost calculations
- **Keeper Enquiries** - Vehicle ownership data
- **Crush Watch / Security Watch** - Asset protection alerts
- **Digital Vehicle Imagery** - Vehicle images

**Sectors:** Dealerships, Fleet/Leasing, Insurance, Manufacturers, Lenders, Auctions

**Integration:** API access available for business customers. Uses the cap Code as a universal vehicle identifier.

**Note:** CAP HPI is the dominant B2B provider in the UK automotive industry. Almost all dealer groups, finance houses, and insurers use their data. Pricing is enterprise-level and negotiated individually.

### 4b. Experian AutoCheck
**URL:** https://www.experian.co.uk/business-products/autocheck/
**Type:** B2B and B2C
**Cost:** Consumer: £6.99/single check, £14.99/5 checks; B2B: Custom pricing

**Data provided:**
- Outstanding finance status and details
- Insurance write-off status and category
- Stolen vehicle check (PNC data)
- DVLA status (imported, exported, scrapped)
- Mileage discrepancy alerts
- Vehicle identity verification
- £30,000 data guarantee (via One Auto API integration)

**Data Sources:** DVLA, Police National Computer, SMMT, Finance companies, Insurance companies (via MIAFTR/Navigate)

**Integration:** Available via API for business systems including online retail, insurance underwriting, and parts ordering.

### 4c. MyCarCheck (CDL Vehicle Information Services)
**URL:** https://www.mycarcheck.com/
**Type:** B2C and B2B
**Cost:** Free basic check; paid checks for finance/stolen/write-off

Powered by CDL Vehicle Information Services Ltd - the UK's leading provider of VRM and DVLA vehicle look-up services to the insurance industry.

### 4d. CarAnalytics
**URL:** https://www.caranalytics.co.uk/
**Type:** B2C and B2B API
**Cost:** Consumer: Basic check £0.99, Full check £10.99; Trade: from £2/check

**API features:**
- VRM Lookup
- Vehicle History Check
- DVLA Data integration
- Comprehensive vehicle data (make, model, MOT history)
- 80+ data points including stolen, finance, write-off, salvage

Data powered by DVLA, DVSA, SMMT, Experian, and verified partners.

---

## 5. Market Pricing & Valuation Data Sources

### 5a. AutoTrader Valuations
**URL:** https://www.autotrader.co.uk/partners/retailer/auto-trader-connect
**Type:** B2B (official API); Scraping (unofficial)

**Official API (AutoTrader Connect):**
- Vehicles API, Stock API, Valuations API
- Live market valuations
- Retail Rating, Average days to sell, Competitor View
- Trended Valuations (6 months historic + 6 months forecast)
- Accuracy: ~5% at 6 months, ~3% at 3 months, ~1% at 1 month
- **Cost:** Expensive - requires trade advertising package, likely £1,000+/month
- **Restrictions:** Endpoints only available to users with direct Autotrader licence

**Scraping Options (via Apify):**
- Apify AutoTrader.co.uk scrapers: ~$0.85 per 1,000 cars
- Extracts: title, price, mileage, year, location, seller info, images, specs
- Multiple scraper actors available on Apify platform
- Piloterr Autotrader Listing API also available
- **Legal note:** Scraping AutoTrader may violate their ToS

### 5b. Percayso Vehicle Intelligence (formerly Cazana)
**URL:** https://percayso-vehicle-intelligence.co.uk/
**Type:** B2B API
**Cost:** Custom pricing (contact sales)

**Data:**
- 700,000+ unique retail advert prices processed daily
- 12,000+ trade and private classified sources aggregated every 24 hours
- 1 billion+ live and historic vehicle adverts
- 'Retail Back' methodology using advanced data science and ML
- Valuations at VRM and VIN levels
- Real-time data processing

**Use cases:** Automotive lending, insurance, manufacturing, fleet sectors

### 5c. CAP HPI Black Book
**URL:** https://www.cap-hpi.com/solutions/valuations/
**Type:** B2B
**Cost:** Enterprise pricing

- **Black Book Live** - Real-time trade and retail valuations
- **Black Book +12** - 12-month forward forecasts
- **Gold Book / Gold Book iQ** - Longer-term residual value forecasts
- Industry benchmark for used car trade values in the UK

### 5d. Brego
**URL:** https://brego.io/products/api
**Type:** B2B API
**Cost:** Custom pricing (free trial available)

**Key features:**
- 30 million+ API calls/month served
- 100ms response time (some claims of under 50ms)
- Up to 96 months of depreciation data
- AI-powered depreciation and valuation predictions
- Historic, current, and future valuations
- Covers cars, vans, motorbikes, caravans, motorhomes, HGVs, agricultural vehicles
- Full REST JSON API, implementation in <5 minutes

### 5e. eBay Motors Scraping
**Type:** Scraping only (no official API for UK car data)

**Available tools:**
- Oxylabs eBay Scraper API
- Apify eBay Items Scraper
- ScraperAPI eBay Scraper
- ZenRows eBay Scraper

**Data extractable:** Prices, descriptions, images, location, availability, seller info, vehicle specs
**Formats:** JSON, XML, CSV, Excel

**Legal note:** Scraping permitted for public data not behind login walls, but professional legal advice recommended.

### 5f. Other Marketplace Data
- **Cazoo** (relaunched April 2025 as dealer marketplace under MOTORS): 258,000+ vehicles, 5,000+ dealers. No public API known.
- **Motorway** (trade/wholesale platform): No public API.
- **cinch** (Constellation Automotive Group): No public API.
- **Facebook Marketplace / Gumtree**: Scraping only, highly restricted.

---

## 6. Vehicle Identification / VIN Decoding

### 6a. NHTSA vPIC API (Free - US-focused but useful)
**URL:** https://vpic.nhtsa.dot.gov/api/
**Cost:** FREE - no registration required
**API:** Yes (REST)

- 25+ API endpoints
- Available 24/7
- Primarily for US-market vehicles (Model Years 1981+)
- Limited results for non-US vehicles
- Decodes make, model, year, body type, engine, drivetrain
- Current version 3.66 (updated Nov 2025)

**Limitation:** UK-spec vehicles may return limited data.

### 6b. Vindecoder.eu / Vincario
**URL:** https://vindecoder.eu/api/ (now transitioning to https://vincario.com/)
**Cost:** Paid (tiered plans - contact for pricing)
**API:** Yes (REST/JSON)

- Extended European and North American vehicle support
- Covers cars, vans, trucks, buses, trailers, motorbikes, tractors
- 99.9% API uptime
- Full REST JSON API

### 6c. SMMT (Society of Motor Manufacturers and Traders)
**URL:** https://www.smmt.co.uk/vehicle-data/
**Type:** B2B data provider

- UK new car registration data and statistics
- Vehicle identification via SMMT codes
- **CarweB** service (collaboration between SMMT and Piper Group)
- Provides the authoritative UK vehicle specification database
- Used by many downstream data providers

**Note:** SMMT data underpins most UK vehicle identification. Their data feeds into CAP HPI, Experian, and other providers. Direct access is typically enterprise-level.

### 6d. CAP Code System
**URL:** Via CAP HPI
**Type:** B2B

The cap Code is the industry-standard vehicle derivative identifier in the UK. Every version/trim of every vehicle gets a unique cap Code. This is used across the automotive industry to precisely identify vehicles and link to valuation/specification data.

---

## 7. Insurance Write-Off Databases

### 7a. MIB Navigate (formerly MIAFTR)
**URL:** https://www.mib.org.uk/managing-insurance-data/mib-managed-services/cue-miaftr/
**Type:** Restricted access
**Cost:** Subscription-based (insurers and authorised bodies)

**Key change:** From 24 November 2025, MIAFTR has been absorbed into **Navigate** (MIB's new central platform).

**Navigate holds:**
- All insured vehicles in the UK
- Vehicle Salvage & Theft Data (formerly MIAFTR)
- Motor insurance policy data (since 30 April 2024)

**Write-off categories:**
- **Cat A** - Scrap only (must be crushed)
- **Cat B** - Body shell must be crushed, parts may be salvaged
- **Cat S** (formerly Cat C) - Structural damage, repairable
- **Cat N** (formerly Cat D) - Non-structural damage, repairable

**Access:** Only available to subscribers: police, insurers, and those working on behalf of existing subscribers. Public cannot access directly.

**How to check as a consumer/business:** Through authorised vehicle check providers (CAP HPI, Experian AutoCheck, etc.) who have subscription access.

### 7b. CUE (Claims and Underwriting Exchange)
**URL:** https://www.mib.org.uk/managing-insurance-data/mib-managed-services/cue-miaftr/
**Type:** Restricted access

- 40+ million claims records from UK insurers
- Motor, home, travel, and personal injury incidents
- Managed by Insurance Database Services Limited (IDSL)
- Used by insurers for underwriting and fraud detection
- **Not directly accessible** for vehicle check services

---

## 8. Finance / Outstanding Finance Checks

### How Outstanding Finance Data Works in the UK

There is **no single public database** for outstanding vehicle finance. Data comes from:

1. **Finance companies** who register their interest with providers like:
   - Experian (via AutoCheck)
   - CAP HPI (via hpi check)
   - Various other vehicle check services

2. **Key providers who aggregate finance data:**
   - **Experian** - Major credit reference agency, largest finance data holder
   - **CAP HPI** - Industry standard, backed by guarantee
   - **MyCarCheck** (CDL) - Partners with multiple finance companies
   - **Total Car Check** - Finance data via Experian

### Access for a Car Check Service

You cannot access outstanding finance data directly. You must:
1. Partner with Experian, CAP HPI, or similar authorised data provider
2. Pay per-check fees (typically £2-7 per check at trade rates)
3. Some providers offer API integration

**Guarantees:** Most providers offer a financial guarantee (e.g., Experian's £30,000 guarantee) if they fail to identify outstanding finance.

---

## 9. Stolen Vehicle Databases

### 9a. Police National Computer (PNC)
**Type:** Restricted - law enforcement only
**Direct access:** NOT available to the public or businesses

The PNC is the authoritative database for stolen vehicles in the UK. Only licensed vehicle-checking providers can legally access theft markers.

### 9b. NMPR (National Mobile Property Register)
**URL:** https://www.immobilise.com/
**Type:** Public registration, police access for searching

- Free property registration service used by police
- Can register vehicle details, tools, etc.
- Police use it to check recovered property

### 9c. How to Access Stolen Vehicle Data

Through authorised intermediaries only:
- **CAP HPI** - Checks PNC stolen markers
- **Experian AutoCheck** - Checks PNC stolen markers
- **One Auto API** (via Experian) - Stolen check endpoint
- **CarAnalytics** - Stolen vehicle check

**Cost:** Typically included in full vehicle check packages (£2-11 per check)

---

## 10. Recall Data

### 10a. DVSA Vehicle Recalls API (ARCHIVED)
**URL:** https://github.com/dvsa/vehicle-recalls-api
**Status:** Repository ARCHIVED on May 8, 2025 (read-only)

**Endpoint:** `GET /recalls?make={make}&vin={vin}`

**Response codes:**
- 200: Success (recall exists or not)
- 400: Missing parameters
- 422: Invalid VIN/make (SMMT validation)
- 403: Unauthorized

**Authentication:** Required SMMT API key

**Note:** This API is now archived. Current recall data is available through:

### 10b. MOT History API (Partial Recall Data)
Some manufacturers share recall data with DVSA, accessible via the MOT History API:
- MAN Trucks
- Ford
- Mercedes
- VW Vans

### 10c. GOV.UK Recall Search Service
**URL:** https://www.check-vehicle-recalls.service.gov.uk/
**Type:** Web service (no public API)

Allows searching for vehicle recalls by make. Can be scraped but no official API.

### 10d. data.gov.uk Recalls Dataset
**URL:** https://www.data.gov.uk/dataset/18c00cf3-3bb2-4930-b30d-78113113aaa7/vehicle-safety-branch-recalls-database
**Status:** OUTDATED - Last updated February 2016

### 10e. One Auto API Recall Check
**URL:** https://www.oneautoapi.com/solution/vehicle-recall-check-api/
**Type:** Commercial API
Provides recall check as a service endpoint.

---

## 11. Emissions / ULEZ / Clean Air Zone Data

### 11a. DVLA VES API (Primary Source)
The DVLA VES API (see Section 2) provides the key emissions fields:
- `euroStatus` - Euro emissions standard (Euro 1-6)
- `co2Emissions` - CO2 in g/km
- `realDrivingEmissions` - RDE value
- `fuelType` - Petrol, Diesel, Electric, etc.
- `typeApproval` - Type approval category

**This is sufficient to determine ULEZ/CAZ compliance** using these rules:
- Petrol: Must be Euro 4+ (generally 2006+)
- Diesel: Must be Euro 6+ (generally 2015+)
- Electric/Hydrogen: Always compliant

### 11b. TfL ULEZ Vehicle Compliance Checker
**URL:** https://tfl.gov.uk/modes/driving/check-your-vehicle/
**Type:** Web tool only (NO public API)

**Important:** The TfL `vehicle/ulezcompliance` API endpoint was **taken down** (confirmed in TfL Tech Forum). There is no current public API for programmatic ULEZ compliance checking.

**Data sources used by TfL:** DVLA, VCA (Vehicle Certification Agency), manufacturer data.

**Workaround:** Use DVLA VES API `euroStatus` and `fuelType` fields to calculate ULEZ compliance yourself. The rules are straightforward and well-documented.

### 11c. GOV.UK Clean Air Zone Checker
**URL:** https://www.gov.uk/clean-air-zones
**Checker:** https://vehiclecheck.drive-clean-air-zone.service.gov.uk/
**Type:** Web service, managed by JAQU (Joint Air Quality Unit)
**API:** No public API available

**Active Clean Air Zones (2025-2026):**
- London ULEZ (all 32 boroughs since Aug 2023)
- Birmingham CAZ (Class D, since June 2021 - charges rising Aug 2025)
- Bath CAZ (Class C)
- Bradford CAZ (Class C)
- Bristol CAZ (Class D)
- Portsmouth CAZ (Class B)
- Sheffield CAZ (Class C)
- **Manchester:** Confirmed NOT proceeding with CAZ (Jan 2025)

**Workaround:** Same as ULEZ - use DVLA euroStatus to calculate compliance per zone class.

### 11d. TfL Unified API (General Transport Data)
**URL:** https://api.tfl.gov.uk/
**Developer portal:** https://api-portal.tfl.gov.uk/
**Cost:** FREE (500 requests plan)
**API:** Yes (REST)

Provides London transport data but **NOT vehicle compliance checking**. Useful for journey planning, congestion data, etc. Not directly relevant for a car check service.

---

## 12. Aggregator APIs (One-Stop-Shop Providers)

These providers aggregate multiple data sources into single API platforms, which may be the most practical approach for a car check service.

### 12a. One Auto API
**URL:** https://www.oneautoapi.com/
**Cost:** Custom pricing (free testing available)

**Aggregated data sources include:**
- DVLA vehicle data
- Experian AutoCheck (stolen, finance, write-off with £30,000 guarantee)
- Brego valuations
- Percayso (Cazana) valuations
- AutoTrader valuations (requires separate licence)
- Marketcheck data

**Available endpoints:**
- Vehicle Details from VRM (low latency DVLA lookup, keeper and plate changes)
- Vehicle & Model Details from VRM (extended model details, battery/charge data)
- Stolen Check from VRM
- Scrap Marker Check from VRM
- Keeper Check from VRM
- Vehicle Recall Check
- Vehicle Valuations
- Car Specification data

**Coverage:** 200,000+ car, EV, and LCV derivatives in the UK market.

### 12b. UK Vehicle Data
**URL:** https://ukvehicledata.co.uk/
**Cost:** PAYGO or Monthly subscription

**PAYGO Pricing (pre-payment):**

| Tier | Credit | Vehicle Data | MOT History | Battery Data |
|---|---|---|---|---|
| 1 | £50 | £0.15/lookup | £0.068 | £0.086 |
| 2 | £150 | £0.12 | £0.053 | £0.062 |
| 3 | £249 | £0.083 | £0.046 | £0.054 |
| 4 | £495 | £0.068 | £0.022 | £0.041 |
| 5 | £995 | £0.042 | £0.024 | £0.024 |

**Monthly Subscription:**

| Plan | Monthly | Vehicle Data | MOT History | Battery Data |
|---|---|---|---|---|
| Small | £99 | £0.081 | £0.042 | £0.081 |
| Medium | £250 | £0.064 | £0.038 | £0.064 |
| Large | £495 | £0.041 | £0.022 | £0.059 |
| XL | £995 | £0.024 | £0.019 | £0.042 |
| WOPR | £1,995 | £0.011 | £0.005 | £0.029 |

Credits valid for 12 months. No setup fee. Up to 75% saving over PAYGO with subscriptions.

**APIs available:** Vehicle data, MOT history, battery data
**Documentation:** https://ukvehicledata.co.uk/ApiDocumentation

### 12c. Vehicle Smart
**URL:** https://vehiclesmart.com/vehicle-smart-api.html
**Type:** B2B API
**Cost:** Contact for pricing

Powers mobile apps, websites, and web services with DVLA and DVSA vehicle data.

### 12d. Rapid Car Check
**URL:** https://www.rapidcarcheck.co.uk/uk-vehicle-history-data-api-apps-websites/
**Cost:** Monthly plans

| Plan | Monthly Checks | Price |
|---|---|---|
| Starter | 50 | £4.99+VAT |
| Basic | 100 | £9.99+VAT |
| Standard | 500 | £14.99+VAT |
| Pro | 1,000 | £27.99+VAT |
| Business | 2,000 | £54.99+VAT |
| Enterprise | 5,000 | £129.99+VAT |
| Ultimate | 10,000 | £259.99+VAT |

Includes WordPress plugin for easy integration.

### 12e. Check Car Details
**URL:** https://api.checkcardetails.co.uk/
**Type:** Vehicle Data API
**Cost:** Contact for pricing

VRM Lookup Database for UK vehicles.

---

## 13. Summary: Recommended Architecture

### Tier 1: Free Government APIs (Must-Have)

| Source | Data | Cost | Priority |
|---|---|---|---|
| **DVLA VES API** | Tax, MOT status, make, model, fuel, emissions, colour, V5C date | Free/~2p | CRITICAL |
| **DVSA MOT History API** | Full MOT history, mileage readings, advisories, failures | Free | CRITICAL |
| **DVSA Open Data** | Anonymised MOT bulk data for analytics/ML | Free | HIGH |

### Tier 2: Essential Paid Data (Required for Full Car Check)

| Source | Data | Approx Cost | Priority |
|---|---|---|---|
| **Experian/CAP HPI** (via aggregator) | Stolen check, finance check, write-off status | £2-7/check | CRITICAL |
| **Valuation provider** (Brego/Percayso/CAP) | Market value, depreciation forecast | £0.05-0.50/check | HIGH |
| **VIN decoder** | Full vehicle specifications from VIN | £0.02-0.10/decode | MEDIUM |

### Tier 3: Market Data (For Pricing Features)

| Source | Data | Method | Priority |
|---|---|---|---|
| **AutoTrader** | Live listing prices, days-to-sell | Scraping or API (expensive) | HIGH |
| **eBay Motors** | Sold prices, auction data | Scraping | MEDIUM |
| **Cazoo/cinch** | Dealer listing prices | Scraping | LOW |

### Tier 4: Derived/Calculated Data (Build Yourself)

| Feature | Source Data | Method |
|---|---|---|
| ULEZ/CAZ compliance | DVLA euroStatus + fuelType | Rule-based calculation |
| Mileage anomaly detection | MOT History odometer readings | Statistical analysis |
| Condition scoring | MOT advisories + failures | ML/scoring algorithm |
| Price fairness | Valuations vs listing price | Comparison algorithm |

### Recommended Starting Stack

For an MVP car check service, the most practical approach would be:

1. **DVLA VES API** (free) - Basic vehicle data
2. **DVSA MOT History API** (free) - MOT history and mileage
3. **UK Vehicle Data** or **One Auto API** (aggregator) - Adds stolen/finance/write-off checks, valuations, and specs through a single integration point
4. **DVSA Open Data** (free) - Bulk MOT data for building analytics and ML models
5. **AutoTrader scraping** (via Apify, ~$0.85/1000) - Market pricing comparison data

This gives comprehensive coverage while keeping costs manageable. The two free government APIs provide enormous value, and a single aggregator API fills in the commercial data gaps.

---

## Key URLs Reference

| Resource | URL |
|---|---|
| DVSA MOT History API Docs | https://documentation.history.mot.api.gov.uk/ |
| DVSA MOT API Registration | https://documentation.history.mot.api.gov.uk/mot-history-api/register |
| DVLA VES API Portal | https://developer-portal.driver-vehicle-licensing.api.gov.uk/ |
| DVLA VES API Spec | https://developer-portal.driver-vehicle-licensing.api.gov.uk/apis/vehicle-enquiry-service/v1.2.0-vehicle-enquiry-service.html |
| DVSA Open Data | https://open.data.dvsa.gov.uk/ |
| Data.gov.uk (MOT) | https://www.data.gov.uk/dataset/c63fca52-ae4c-4b75-bab5-8b4735e1a4c9/anonymised-mot-tests-and-results |
| GOV.UK Recall Checker | https://www.check-vehicle-recalls.service.gov.uk/ |
| GOV.UK CAZ Checker | https://vehiclecheck.drive-clean-air-zone.service.gov.uk/ |
| TfL ULEZ Checker | https://tfl.gov.uk/modes/driving/check-your-vehicle/ |
| CAP HPI | https://www.cap-hpi.com/ |
| Experian AutoCheck | https://www.experian.co.uk/business-products/autocheck/ |
| One Auto API | https://www.oneautoapi.com/ |
| UK Vehicle Data | https://ukvehicledata.co.uk/ |
| Brego Valuations | https://brego.io/products/api |
| Percayso (Cazana) | https://percayso-vehicle-intelligence.co.uk/ |
| MIB (Navigate/MIAFTR) | https://www.mib.org.uk/ |
| askMID (Insurance check) | https://www.askmid.com/ |
| NHTSA vPIC (Free VIN) | https://vpic.nhtsa.dot.gov/api/ |
| SMMT Vehicle Data | https://www.smmt.co.uk/vehicle-data/ |
| Apify (Scrapers) | https://apify.com/ |
| DVSA Recalls API (Archived) | https://github.com/dvsa/vehicle-recalls-api |
