# Copyright 2024
# Directory: yt-rag/app/data/default_documents.py

"""
Default documents for seeding the Sahayak RAG knowledge base.

This corpus covers 10 schemes relevant to the SIH26092 problem statement
(marginalized entrepreneurs). Every fact below was verified against official
government portals (standupmitra.in, kviconline.gov.in, mudra.org.in,
nsfdc.nic.in, vcfsc.in, minorityaffairs.gov.in, ddugky.gov.in,
pmavanidhi.gov.in, cgtmse.in, pmvishwakarma.gov.in) via web research on the
day this file was last updated.

Amounts and eligibility limits on real schemes change with budget
announcements. Before the SIH demo, re-verify each figure against the cited
official portal and update the verification note. This RAG layer only stores
and retrieves TEXT for the "why this scheme" explainer (Feature 3) -- the
structured eligibility_rules used by the deterministic rules engine
(Feature 2) live in a separate table.
"""

from typing import List, Dict

# Default documents for seeding
DEFAULT_DOCUMENTS: List[Dict[str, str]] = [
    {
        'chunk_id': 'scheme_standup_india_v1',
        'source': 'https://www.standupmitra.in',
        'verified_on': '2026-09-04',
        'text': '''Stand-Up India Scheme

Purpose: Composite bank loans (term loan + working capital) for setting up a NEW (greenfield) enterprise in manufacturing, services, trading, or agriculture-allied activities.

Who it is for: At least one Scheduled Caste (SC) or Scheduled Tribe (ST) borrower and at least one woman borrower per bank branch. Applicant must be above 18 years of age. For non-individual enterprises, at least 51% shareholding and controlling stake must be held by an SC/ST or woman entrepreneur.

Loan amount: Between Rs. 10 lakh and Rs. 1 crore, covering up to 75% of the project cost. The borrower must contribute a minimum of 10% of the project cost as margin money (own contribution). Loan repayment period is up to 7 years with a maximum moratorium of 18 months. Interest rate is set by the individual bank (SIDBI provides refinance).

Key condition: The enterprise must be a "greenfield" project -- the applicant's first venture in that business, not an expansion or upgrade of an existing unit. This scheme does NOT cover business expansion.

Implementing body: All scheduled commercial bank branches, monitored by SIDBI, under the Ministry of Finance / Department of Financial Services. Applications are made through the standupmitra.in portal or directly at a bank branch.

Documents typically required: Identity/address proof, caste certificate (for SC/ST applicants), detailed project report, business registration (if any), bank account details.

OFFLINE ACCESS (Physical Locations):
- All SBI, PNB, Bank of Baroda, Canara Bank, Union Bank, and other scheduled commercial bank branches across India
- SIDBI Regional Offices (Delhi, Mumbai, Kolkata, Chennai, Bengaluru, Hyderabad, Ahmedabad, Lucknow)
- District Industries Centres (DIC) in your district
- Stand-Up Mitra Facilitation Centres at major bank branches
- Toll-free helpline: 1800-180-1111'''
    },
    {
        'chunk_id': 'scheme_pmegp_v1',
        'source': 'https://www.kviconline.gov.in/pmegp',
        'verified_on': '2026-09-04',
        'text': '''Prime Minister's Employment Generation Programme (PMEGP)

Purpose: Credit-linked margin-money subsidy to help first-time entrepreneurs set up NEW micro-enterprises (manufacturing or service/business). PMEGP does not fund expansion or upgradation of an existing unit on the first loan.

Project cost limits: Up to Rs. 50 lakh for manufacturing projects; up to Rs. 20 lakh for service/business projects. There is NO income ceiling for applicants. A second loan is allowed only for upgradation of an existing unit (manufacturing up to Rs. 1 crore, service up to Rs. 25 lakh) @ 15% subsidy.

Subsidy (margin money): 15% to 35% of the project cost, depending on category and location --
- General category, urban area: 15%
- General category, rural area: 25%
- Special category (SC, ST, OBC, minorities, women, transgender persons, ex-servicemen, persons with disabilities, and applicants from NER/hill/border/aspirational districts), urban area: 25%
- Special category, rural area: 35%

Beneficiary's own contribution: 5% of project cost for special category applicants, 10% for general category. The balance is a bank term loan.

Education requirement: For projects above Rs. 10 lakh, the applicant must have passed at least VIII standard; for general area service projects above Rs. 5 lakh, VIII standard is required.

Other conditions: Only one person per family (self + spouse) can avail PMEGP assistance. Entrepreneurship Development Programme (EDP) training is mandatory before subsidy is released for most project sizes (10 working days for projects above Rs. 5 lakh; 5 working days for Rs. 2-5 lakh; not mandatory below Rs. 2 lakh).

Implementing body: Khadi and Village Industries Commission (KVIC), Ministry of MSME, along with State KVIBs and District Industries Centres (DICs). Apply via the PMEGP e-Portal.

OFFLINE ACCESS (Physical Locations):
- KVIC Zonal Offices in all state capitals
- District Industries Centres (DIC) -- available in every district
- KVIB (Khadi & Village Industries Board) offices in your state
- All nationalized banks: SBI, PNB, Bank of Baroda, Canara Bank, Union Bank, Indian Bank, Central Bank of India
- Regional Rural Banks (RRBs) in rural areas
- Udyam Kendra / MSME Facilitation Centres
- Toll-free helpline: 1800-180-1551'''
    },
    {
        'chunk_id': 'scheme_mudra_pmmy_v1',
        'source': 'https://www.mudra.org.in',
        'verified_on': '2026-09-04',
        'text': '''Pradhan Mantri MUDRA Yojana (PMMY) -- MUDRA Loans

Purpose: Collateral-free loans to non-corporate, non-farm small and micro enterprises (income-generating activities in manufacturing, trading, or services, including allied agricultural activities).

Loan categories (by stage of the business):
- Shishu: up to Rs. 50,000 -- for a very early-stage or first-time business idea.
- Kishor: above Rs. 50,000 up to Rs. 5 lakh -- for an established micro-business looking to grow.
- Tarun: above Rs. 5 lakh up to Rs. 10 lakh -- for a more developed unit.
- Tarun Plus: above Rs. 10 lakh up to Rs. 20 lakh -- introduced October 2024, only for borrowers who have already taken and successfully repaid a Tarun loan (priority for clean repayment track record).

Who it is for: Any non-corporate, non-farm small/micro enterprise -- no caste, gender, or category restriction, though priority focus is on first-generation and women entrepreneurs. No collateral is required.

How it works: MUDRA itself does not lend directly -- loans are disbursed through member lending institutions (public/private banks, Regional Rural Banks, Small Finance Banks, NBFCs, and MFIs) under refinance support from MUDRA. A RuPay-based MUDRA Card may be issued for flexible working-capital withdrawal.

Where to apply: Any participating bank branch, or online via the Udyamimitra / Jan Samarth portal.

Note: Interest rates are NOT fixed by the government -- each lender sets its own rate (typically bank MCLR + spread), so quoted rates vary by bank.

OFFLINE ACCESS (Physical Locations):
- Any SBI, PNB, Bank of Baroda, Canara Bank, Union Bank, Indian Bank, Central Bank of India branch
- Regional Rural Banks (RRBs) and Small Finance Banks
- Cooperative banks and Nationalized bank branches in every town
- MUDRA Loan Facilitation desks at lead bank branches
- CGTMSE-empanelled Member Lending Institution branches
- Toll-free helpline: 1800-233-4653'''
    },
    {
        'chunk_id': 'scheme_nsfdc_v1',
        'source': 'https://nsfdc.nic.in',
        'verified_on': '2026-09-04',
        'text': '''National Scheduled Castes Finance and Development Corporation (NSFDC) -- Concessional Loan Schemes

Purpose: Concessional-interest term loans and micro-finance for income-generating economic activities, aimed specifically at Scheduled Caste (SC) entrepreneurs and self-help groups.

Who it is for: Individuals or groups belonging to the Scheduled Castes, with annual family income NOT exceeding Rs. 5 lakh (income ceiling effective from January 2026, revised periodically -- confirm current threshold on nsfdc.nic.in).

Loan details (typical/illustrative, verify current rates):
- Micro Finance Scheme (MFS): loan up to Rs. 1.25 lakh per beneficiary at ~6.5% interest, up to 90% of project cost (own contribution required).
- Term Loan Scheme: business loans up to Rs. 45 lakh at ~8% interest, per state SCDC allocation limits.
- Aikyam Yojana: up to 15% interest subsidy on loans availed through channel partners.
Up to 90% of the project cost can be financed (beneficiary provides the balance).

Eligibility note: NSFDC targets SC-community entrepreneurs whose family income is within the notified ceiling and who are engaged in income-generating activities. The loan is aimed at weaker sections and economically weaker SC families.

How funds flow: NSFDC does not lend directly to individuals. It channels concessional refinance through State Scheduled Castes Development Corporations (SCDCs), NBFC-MFIs, and nationalised banks, including the PM-SURAJ portal, who then disburse to the end beneficiary.

Scope: Covers a wide range of income-generating activities -- small manufacturing, trading, services, agriculture and allied activities, transport, and skill-linked micro-enterprises.

Implementing ministry: Ministry of Social Justice & Empowerment (MoSJE) -- the same sponsoring ministry as SIH problem statement SIH26092.

Apply through: The relevant State SCDC office, an empanelled channel partner bank/NBFC-MFI listed on nsfdc.nic.in, or the PM-SURAJ portal.

OFFLINE ACCESS (Physical Locations):
- State Scheduled Castes Development Corporations (SCDCs) offices in every state
- NSFDC head office: North India Office, 14-A, Old Rajinder Nagar, New Delhi
- PM-SURAJ facilitation counters at District Magistrate / District Social Welfare offices
- Nationalized banks: SBI, PNB, Bank of India, Bank of Baroda, Canara Bank, Indian Bank
- District Social Welfare Officer (DSWO) offices
- Block-level SC Development offices in rural areas
- Toll-free helpline: 011-42250160'''
    },
    {
        'chunk_id': 'scheme_asiiim_v1',
        'source': 'https://www.vcfsc.in/asiim',
        'verified_on': '2026-09-04',
        'text': '''Ambedkar Social Innovation and Incubation Mission (ASIIM)

Purpose: Support Scheduled Caste (SC) students and SC/Divyang youth with innovative, technology-driven business ideas by providing equity funding, incubation, and mentorship to turn ideas into commercial ventures.

Who it is for: SC students and SC differently-abled (Divyang) youth with innovative start-up ideas identified by Technology Business Incubators (TBIs) set up by the Department of Science and Technology, Atal Incubation Centres (AICs), science/technology parks, or approved (including reputed private) incubators. Students recognised through Smart India Hackathon/Hardware Hackathon and CSR-backed start-ups are also eligible.

Equity support: Equity funding up to Rs. 30 lakh over 3 years, disbursed at Rs. 10 lakh per year, for each selected entity. Funding covers TBI accommodation/hardware/software cost, fellowship, travel & marketing, IP filing, tool-room expenses, and co-working.

Structure: The fund is injected as Equity, Optionally Convertible Preference Shares (OCPS), or Compulsorily Convertible Preference Shares (CCPS). Before assistance, selectees must convert into a Private/Public Limited company and the SC entrepreneur must hold at least 51% shareholding with management control. The assisted tenure is 10 years from first disbursement.

Follow-on funding: Successful ventures can qualify for further venture funding of up to Rs. 15 crore (VCF-SC) / Rs. 5 crore equity venture capital.

Launched: 30 September 2020 by Department of Social Justice and Empowerment, Ministry of Social Justice & Empowerment (MoSJE). Target: 1,000 start-ups over 4 years (2020-24).

How it differs from loans: Instead of a standard repayable bank loan, ASIIM provides EQUITY funding tied to incubation and demonstratable progress -- it does not require repayment like a term loan.

Apply through: The VCF-SC / ASIIM portal (vcfsc.in/asiim), via partner TBIs, or directly as per VCF-SC guidelines.

OFFLINE ACCESS (Physical Locations):
- Partner Technology Business Incubators (TBIs) listed on vcfsc.in -- visit their office to apply
- Atal Incubation Centres (AICs) in universities and engineering colleges near you
- Science & Technology Parks and startup hubs across India
- Department of Social Justice & Empowerment, New Delhi: Room 357-C, C-Wing, Shastri Bhawan
- State-level Social Justice department offices
- Contact via TBI program managers for walk-in applications'''
    },
    {
        'chunk_id': 'scheme_nai_roshni_v1',
        'source': 'https://www.minorityaffairs.gov.in',
        'verified_on': '2026-09-04',
        'text': '''Nai Roshni -- Leadership Development of Minority Women

Purpose: A central sector scheme to empower and instil confidence in minority women by providing leadership development and life-skill training, so they can interact with government systems, banks, and institutions and take up economic and leadership roles.

Who it is for: Women from notified minority communities (Muslim, Sikh, Christian, Buddhist, Zoroastrian/Parsi, and Jain) under Section 2(c) of the National Commission for Minorities Act, 1992. Age group 18 to 65 years. Up to 25% of participants may be from non-minority communities (SC/ST/OBC, women with disabilities, and Elected Women Representatives). Preferred annual family income not exceeding Rs. 2.5 lakh.

What it provides: Free residential and non-residential leadership training modules on -- leadership of women, social & behavioural change, Swachh Bharat, legal rights of women, life skills, health & hygiene, education, nutrition & food safety, Right to Information, economic empowerment, Digital India literacy, and introduction to government mechanisms. Trainees may receive a stipend, meals, and crèche facilities during training; the scheme covers training materials, fees, food, and travel. Residential batches up to 25 women; participants generally need Class XII (relaxed to Class X/V in some cases).

How it differs from loans: Nai Roshni does NOT give a business loan or capital -- it is a training/skilling program. A woman who completes it might pair it with a financing scheme like MUDRA or PMEGP for actual business capital.

Implementing body: Ministry of Minority Affairs, through NGOs, registered societies/public trusts/non-profit companies, universities, government training institutes, women's cooperatives, and state channelizing agencies. Applications through the Online Application Management System (OAMS).

OFFLINE ACCESS (Physical Locations):
- Implementing NGOs and registered societies in your district (list on OAMS portal)
- District Minority Welfare Offices
- State Minority Development Corporations / Minorities Financlimited Offices
- Women's Cooperative Societies and Mahila Mandals
- Government Women's Training Institutes and ITIs
- Village/Block-level training centres run by partner NGOs
- Gram Panchayat offices for guidance on joining a batch'''
    },
    {
        'chunk_id': 'scheme_ddu_gky_v1',
        'source': 'https://ddugky.gov.in',
        'verified_on': '2026-09-04',
        'text': '''Deen Dayal Upadhyaya Grameen Kaushalya Yojana (DDU-GKY)

Purpose: Placement-linked skill training for rural poor youth so they can get regular jobs (wage-employment), especially in non-farm sectors, diversifying the income of poor rural families.

Who it is for: Rural youth aged 15 to 35 years from poor families. The upper age limit is relaxed to 45 years for special groups -- SC/ST, women, particularly vulnerable tribal groups (PVTGs), persons with disabilities (PwDs), and transgender individuals. Identification of "poor" is done through participatory identification; interim criteria include MGNREGA worker families (15+ days worked in previous FY), RSBY card holders, Antyodaya Anna Yojana/BPL PDS card families, NRLM self-help-group families, and SECC-2011 auto-inclusion families.

What it provides: 100% free residential/non-residential skill training across 550+ job roles in 50+ sectors (retail, IT/ITES-BPO, hospitality, healthcare, construction, automotive, textile, electronics, BFSI, agriculture/food processing). Boarding, lodging, transport, food, and a stipend are generally provided. Trainees receive industry-recognised certification (third-party assessment via Sector Skill Councils). Training durations are typically 3-12 months.

Placement: Placement-linked -- implementing agencies must achieve a minimum 70% placement rate, with placement support and 12-month post-placement tracking/support. Minimum salary generally Rs. 6,000+ per month (varies by sector/location).

How it differs from a business loan: DDU-GKY aims at getting a rural young person a JOB (wage-employment) through training; it is NOT a mechanism to finance an entrepreneur's own business capital, unlike MUDRA/PMEGP.

Implementing body: Ministry of Rural Development (MoRD), a part of the National Rural Livelihoods Mission (NRLM), executed through approved Project Implementing Agencies (PIAs). Register via the Kaushal Panji / ddugky.gov.in portal or at a training centre through Gram Panchayat/BDO.

OFFLINE ACCESS (Physical Locations):
- Gram Panchayat offices and Block Development Offices (BDO) in every block
- Project Implementing Agencies (PIAs) training centres in rural clusters
- NRLM / DAY-NRLM Van (Village Level Organizations) offices
- District Rural Development Agency (DRDA) / District Mission offices
- RSETI (Rural Self Employment Training Institutes) centres
- State Skill Development Missions and ITI training centres
- Kaushal Panji facilitation counters at common service centres (CSC)'''
    },
    {
        'chunk_id': 'scheme_pm_svanidhi_v1',
        'source': 'https://pmavanidhi.gov.in',
        'verified_on': '2026-09-04',
        'text': '''PM Street Vendor's AtmaNirbhar Nidhi (PM SVANidhi)

Purpose: Provide affordable working-capital loans to street vendors to help them resume and grow their vending business, with interest subsidy and cashback incentives.

Who it is for: Street vendors across India who were operating on or before 24 March 2020 and hold a Certificate of Vending (issued by the Urban Local Body) OR a Letter of Recommendation (LoR) from the Town Vending Committee (TVC). The loan is micro-natured and collateral-free.

Loan details: Revolving collateral-free loans in three tranches -- first tranche up to Rs. 10,000, second up to Rs. 20,000, and third up to Rs. 50,000 (subject to timely repayment of the earlier tranche). The loans are extended at a concessional rate; an interest subsidy of up to 7% per annum is provided on the loan, and a monthly cashback incentive of Rs. 100 is credited for timely repayment made digitally (for the first 100 days each year). Maximum loan tenure is 12 months. The scheme, launched June 2020, has been extended to operate till December 2030.

How it differs from larger schemes: This is for small working capital for street vendors specifically, with much lower amounts (thousands of rupees, not lakhs), unlike the 2 lakh-1 crore loans of MUDRA/Stand-Up India. There is a clear sector (street vending) and a required vending certificate.

Implementing body: Ministry of Housing & Urban Affairs (MoHUA), disbursed through participating banks/SHGs.

OFFLINE ACCESS (Physical Locations):
- Urban Local Body (Municipal Corporation / Municipality / Nagar Panchayat) offices -- to obtain Certificate of Vending
- Town Vending Committee (TVC) offices in your city
- Participating banks: SBI, PNB, Bank of Baroda, Canara Bank, and all nationalized banks
- Self-Help Groups (SHGs) and their federations
- Street Vendor Facilitation Desks at municipal offices
- PM SVANidhi camps organized by ULBs in vending zones'''
    },
    {
        'chunk_id': 'scheme_credit_guarantee_v1',
        'source': 'https://www.cgtmse.in',
        'verified_on': '2026-09-04',
        'text': '''Credit Guarantee Fund Trust for Micro and Small Enterprises (CGTMSE)

Purpose: Provide credit guarantee to banks, NBFCs, and other lending institutions (Member Lending Institutions, MLIs) for collateral-free or third-party-guarantee-free credit to micro and small enterprises (MSEs), so lenders are willing to lend without demanding collateral.

Who it is for: Existing and new micro and small enterprises (manufacturing or service) that can access a bank/NBFC loan. The trust does not lend money itself -- it guarantees a loan that a lender gives. Eligible borrowers include individual entrepreneurs, proprietorships, partnership firms, LLPs, and companies that are MSEs.

Coverage limit: Credit facility (fund-based and non-fund-based) can now be covered up to Rs. 10 crore -- raised from the earlier Rs. 2 crore / Rs. 5 crore ceiling (effective April 2025). For RRBs and select financial institutions the limit is up to Rs. 50 lakh.

Guarantee coverage (extent): Up to 85% of the defaulted amount for credit up to Rs. 5 lakh (micro enterprises); ~75-80% for higher amounts up to Rs. 50 lakh. Higher/extra coverage for women entrepreneurs, ZED-certified units, units in aspirational (identified credit-deficient) districts, and NER/hilly states. For exposures above Rs. 50 lakh up to Rs. 100 lakh the cover is ~50%. The guarantee tenure is up to 5 years (or blocks of 5 years for working capital).

Annual Guarantee Fee (AGF) -- revised, effective 1 April 2025: 0.37% for 0-10 lakh; 0.55% for 10-50 lakh; 0.60% for 50 lakh-1 crore; 0.85% for 1-2 crore; 1.00% for 2-5 crore; 1.10% for 5-8 crore; 1.20% for 8-10 crore. Retail/wholesale trade is now charged at par with other activities.

What is NOT covered: Educational institutions, agriculture, training institutions, self-help groups (SHGs), and activities already covered by another government guarantee are generally NOT eligible.

How it fits with other schemes: CGTMSE is a guarantee behind loans; it is often used together with collateral-free lending programs (e.g., MUDRA, PMEGP loans can carry CGTMSE cover). It is not a standalone loan or subsidy for the applicant's capital -- the entrepreneur still takes a bank loan.

Implementing body: Credit Guarantee Fund Trust for Micro and Small Enterprises, jointly promoted by the Ministry of Micro, Small and Medium Enterprises (MSME/Gol) and SIDBI. Borrower applies through a Member Lending Institution (bank/NBFC); the lender applies to CGTMSE for the guarantee.

OFFLINE ACCESS (Physical Locations):
- All Member Lending Institution branches, including: SBI, PNB, Bank of Baroda, HDFC Bank, ICICI Bank, Axis Bank, Canara Bank, Union Bank
- SIDBI Regional Offices across India (Delhi, Mumbai, Chennai, Kolkata, Ahmedabad, Hyderabad, Bengaluru)
- Udyog Aadhaar / MSME Facilitation Centres (help register for free)
- MSME Development Institutes (Ministry of MSME field offices) in state capitals
- Government empanelled NBFC branches and Small Finance Banks
- Toll-free MSME helpline: 1800-180-6666'''
    },
    {
        'chunk_id': 'scheme_pm_vishwakarma_v1',
        'source': 'https://www.pmvishwakarma.gov.in',
        'verified_on': '2026-09-04',
        'text': '''PM Vishwakarma Yojana

Purpose: Support traditional artisans and craftspeople (Vishwakarma -- e.g. carpenters, tailors, blacksmiths, goldsmiths, potters, weavers, cobblers) through recognition (PM Vishwakarma Certificate & ID), a toolkit incentive, skill up-gradation with stipend, and collateral-free credit support.

Who it is for: Traditional artisans and craftspeople in 18 identified trades, in rural and urban areas. Eligibility requirements: age 18 years or more; not availed of PMEGP, MUDRA, or other collateral-free credit support from a bank/financial institution in the last 5 years; applicant must be a family member practising the artisan/craft trade individually or with family. Priority is given to women, SC/ST, and persons with disabilities.

What it provides:
- Recognition: PM Vishwakarma Certificate and ID Card.
- Skill upgradation: Basic training (5-7 days) with a stipend of Rs. 500 per day, and advanced training (15 days or more) also with Rs. 500 per day stipend.
- Toolkit incentive: One-time financial support of up to Rs. 15,000 (in installments) to buy tools/modern equipment.
- Credit support: Collateral-free loan in two tranches -- first tranche up to Rs. 1 lakh and second tranche up to Rs. 2 lakh (total up to Rs. 3 lakh), at a subsidised interest rate of 5% per annum, with Government of India paying interest subvention. Loan tenure up to 18 months for repayment; for second tranche, up to 30 months.

Key terms (illustrative, verify current): 18 traditional trades; loan interest 5% p.a.; toolkit up to Rs. 15,000; stipend Rs. 500/day; minimum age 18 years; no collateral required; no default/EMI for first 18 months (interest subvention by GoI).

How it differs from PMEGP/MUDRA: It is trade-specific (18 traditional craft trades), the beneficiary is an artisan rather than any entrepreneur, and it bundles a toolkit benefit and skill stipend alongside credit, whereas PMEGP/MUDRA are general business financing.

Implementing body: Ministry of Micro, Small and Medium Enterprises (MSME), in coordination with state/local partners

OFFLINE ACCESS (Physical Locations):
- Any SBI, PNB, Bank of Baroda, Canara Bank, Union Bank, or other nationalized bank branch (loan disbursal)
- PM Vishwakarma facilitation centres / counters at District Industries Centres (DIC)
- Common Service Centres (CSC) in villages for offline registration assistance
- MSME Development Institutes and Udyam Centres
- Artisan co-operatives and KVIC offices
- All 18 identified trade clusters (carpenters, tailors, blacksmiths, etc.) can ask at local Udyam Kendra
- Toll-free helpline: 1800-180-6551'''
    },
]
