# 📖 Master Glossary — 500+ Terms for the Custody, Product and Technology Executive

## How to use this glossary

This glossary is a working reference, not a reading assignment. It is organized by **theme**, not alphabetically across the whole book, because that is how the vocabulary will hit you: a settlements review will throw twenty trade-lifecycle terms at you at once; an architecture review will do the same with technology terms. Within each section, terms are alphabetical.

Three suggested modes of use:

1. **Before a meeting** — skim the one or two sections matching the agenda (e.g., Corporate Actions + Payments before an asset-servicing operations review).
2. **After a meeting** — look up every term you heard but could not have defined. Write it down during the meeting; look it up the same day.
3. **Weekly drill** — during your first 30 days, master the "Top 50" list below, then work through one section per week.

Every definition is self-contained: acronyms are expanded inside their own definitions, and no entry requires you to have read another entry first. The third column — *Why it matters to you* — ties the term to your specific seat: VP of Product Development for Digital Experience at a custodian bank, where your products are the portals, dashboards, APIs and data experiences through which institutional clients consume custody, fund services and analytics.

## Table of contents

1. [Custody and Asset Servicing](#1-custody-and-asset-servicing)
2. [Trade Lifecycle and Settlement](#2-trade-lifecycle-and-settlement)
3. [Fund Accounting, NAV and Fund Structures](#3-fund-accounting-nav-and-fund-structures)
4. [Corporate Actions](#4-corporate-actions)
5. [Payments, SWIFT and Cash](#5-payments-swift-and-cash)
6. [Markets, Instruments and Reference Data](#6-markets-instruments-and-reference-data)
7. [Regulation, Risk and Compliance](#7-regulation-risk-and-compliance)
8. [Product Management and UX](#8-product-management-and-ux)
9. [Technology and Architecture](#9-technology-and-architecture)
10. [Data, Analytics and AI](#10-data-analytics-and-ai)
11. [Leadership, Finance and Corporate Vocabulary](#11-leadership-finance-and-corporate-vocabulary)

## Top 50 terms to master first

If you learn nothing else in week one, learn these. They are the terms most likely to appear in your first ten meetings, grouped by theme:

**The business you serve:** 1. Custodian · 2. Sub-custodian · 3. AUC/A · 4. Asset servicing · 5. Transfer agency · 6. Fund administration · 7. Securities lending · 8. Collateral · 9. Repo · 10. Depositary

**The plumbing:** 11. Trade lifecycle · 12. DvP · 13. T+1 · 14. Settlement fail · 15. SSI · 16. STP · 17. Reconciliation · 18. CSD · 19. T2S · 20. Nostro

**Fund servicing:** 21. NAV · 22. ABOR vs IBOR · 23. NAV error · 24. Swing pricing · 25. ETF creation/redemption · 26. Share class

**Messages and money:** 27. SWIFT · 28. ISO 20022 · 29. MT564 · 30. pacs.008 · 31. Corporate action · 32. Ex-date/record date/pay date

**The rulebook:** 33. CSDR · 34. DORA · 35. BCBS 239 · 36. Three lines of defense · 37. RCSA · 38. KRI · 39. G-SIB · 40. KYC/AML

**Your craft:** 41. North star metric · 42. JTBD · 43. Discovery · 44. PRD · 45. GTM · 46. OKR

**Your platform:** 47. Event-driven architecture · 48. SLO/error budget · 49. Data lineage · 50. RAG (retrieval-augmented generation)

---

## 1. Custody and Asset Servicing

| Term | Definition | Why it matters to you |
|---|---|---|
| Account operator | An entity authorized to send instructions and receive reporting on a custody account on behalf of the account owner, such as an outsourced middle office or investment manager. | Your entitlement model must support operators acting for owners. |
| Actual settlement date accounting (ASDA) | A convention in which a custodian credits or debits client cash and securities positions only when a trade actually settles in the market. | Explains why two clients see different balances for the same activity. |
| Agency securities lending | A program in which the custodian, acting as agent rather than principal, lends clients' securities to borrowers in exchange for collateral and a fee split with the client. | A major revenue line whose dashboards and disclosures you productize. |
| Agent bank | A local bank appointed to perform settlement, safekeeping and asset servicing in a specific market on behalf of a global custodian. | Data quality in your portal is only as good as the agent-bank feed. |
| Asset owner | The institution that ultimately owns invested assets — pension funds, sovereign wealth funds, insurers, endowments — as distinct from the managers it hires. | A core client persona with distinct reporting and oversight needs. |
| Asset servicing | The umbrella term for post-trade services performed on held assets: income collection, corporate actions, tax, proxy voting and related reporting. | The product family your digital experiences must make legible. |
| AUC/A (assets under custody and/or administration) | The total market value of client assets a custodian safekeeps (custody) and/or performs accounting and administration for (administration); State Street's headline scale metric, measured in the tens of trillions. | The denominator behind pricing, league tables and every earnings call. |
| Beneficial owner | The party entitled to the economic benefits of a security — dividends, voting rights, sale proceeds — even when the security is registered in another name for safekeeping. | Drives disclosure, proxy and tax features in client-facing tools. |
| Borrower default indemnification | A custodian's contractual promise to make a securities-lending client whole if a borrower defaults and the collateral is insufficient to replace the loaned securities. | A risk feature clients scrutinize; surfaces in lending dashboards. |
| Cash sweep | The automated daily movement of idle client cash balances into an interest-bearing vehicle such as a money market fund or deposit program. | A yield feature clients expect to configure and monitor digitally. |
| Central securities depository (CSD) | The market-level institution that holds securities in electronic form and operates the final settlement of trades in those securities, such as DTC in the United States or Euroclear France. | The end of the custody chain; source of settlement truth in your data. |
| Class action processing | The service of identifying client eligibility for securities class-action settlements, filing claims and distributing recoveries. | A long-tail service clients expect to track through the portal. |
| Collateral management | The selection, valuation, movement and monitoring of assets pledged to secure exposures such as securities loans, repurchase agreements and derivatives margin. | A growth product with heavy demand for real-time digital views. |
| Common depository | A bank appointed jointly by the international central securities depositories Euroclear and Clearstream to safekeep physical or global note securities on their behalf. | Explains odd custody-chain hops in Eurobond holdings data. |
| Contractual settlement date accounting (CSDA) | A convention in which the custodian credits client accounts on the contractually agreed settlement date regardless of whether the market trade has actually settled, taking the timing risk itself. | A service differentiator that shapes what balances your UI shows. |
| Corporate trust | Trustee and agency services for debt issuance — paying agent, escrow, bond trustee — performed for issuers rather than investors. | Adjacent business line; occasionally shares your platform rails. |
| Custodian | A regulated financial institution that safekeeps clients' financial assets, settles their trades, collects income and services the assets; State Street's core identity. | The business model everything you build ultimately serves. |
| Custody chain | The sequence of intermediaries between an investor and the issuer of a security: global custodian, sub-custodian, central securities depository, registrar. | Explains data latency and breaks your users complain about. |
| Depositary (fund depositary) | Under European fund law, the entity responsible for safekeeping a fund's assets and overseeing its cash flows and compliance with its rules; a fiduciary role beyond plain custody. | European clients hold you to depositary-grade oversight reporting. |
| Depot account | A securities account held at a central securities depository or sub-custodian in which positions are maintained, as distinct from the cash (nostro) account beside it. | The atomic unit of position data in your platforms. |
| Direct custody | A model in which the custodian holds assets through its own local branch or membership of a market's depository rather than through a third-party agent bank. | Direct markets deliver richer, faster data to your products. |
| ETF servicing | The bundle of custody, fund accounting, basket calculation and order-taking services supporting exchange-traded funds and their authorized participants. | State Street services a huge share of world ETF assets; key client base. |
| Fund administration | Outsourced operational services for investment funds: accounting, net asset value calculation, financial reporting, expense management and regulatory filings. | The "A" in AUC/A and a major source of the data you visualize. |
| Global custodian | A custodian offering safekeeping and asset servicing across many markets through a single relationship, operating via a network of sub-custodians and depositories. | State Street's role; your portal is its primary shop window. |
| ICSD (international central securities depository) | A depository — Euroclear Bank or Clearstream Banking Luxembourg — that settles internationally traded securities such as Eurobonds across borders. | A distinct settlement route your data model must represent. |
| Income collection | The custody service of capturing, claiming and crediting dividends, interest and other entitlements owed on held securities. | Clients judge custodians on income timeliness shown in your UI. |
| Indirect holding system | The prevailing legal structure in which investors hold securities through tiers of intermediaries' book entries rather than directly on an issuer's register. | The legal reason positions are "book entries" in your database. |
| Intrinsic value lending | A securities-lending style that lends only the hard-to-borrow securities commanding high fees, rather than lending broadly for volume. | Client program choices you must reflect in lending analytics. |
| Market advocacy | A custodian's engagement with regulators, depositories and market bodies to improve local market practice on behalf of clients. | Source of the market-change notices your portal publishes. |
| Middle-office outsourcing | The delegation of an asset manager's post-trade functions — trade matching, position keeping, reconciliation, performance data — to a provider such as a custodian. | Expands your user base from back office to the manager's front line. |
| Network management | The custodian function that selects, contracts with, monitors and risk-reviews sub-custodians and cash correspondents across markets. | Owner of the market-by-market data you surface in market guides. |
| Nominee | The legal entity in whose name securities are registered for safekeeping purposes while the client retains beneficial ownership. | Explains why registered names differ from client names in data. |
| Omnibus account | A single account at a depository or sub-custodian that commingles the positions of many underlying clients, segregated only on the custodian's own books. | Drives the aggregation and allocation logic in position reporting. |
| Prime custody | A hybrid service for hedge funds that combines custody of unencumbered long assets with financing relationships at prime brokers. | A hedge-fund persona whose portal needs span custody and financing. |
| Proxy voting services | The capture of shareholder-meeting announcements, distribution of ballots to clients, and lodging of their voting instructions with issuers. | Governance-focused clients want a seamless digital voting flow. |
| Reconciliation | The systematic comparison of two records — e.g., custodian books versus depository statements, or cash ledger versus nostro statement — to find and resolve differences (breaks). | Break volumes are a top driver of ops cost your tools can cut. |
| Registrar | The entity maintaining an issuer's official record of security holders and processing transfers of registered ownership. | The ultimate source of record in registered markets. |
| Relief at source | A tax arrangement in which the correct reduced treaty rate of withholding tax is applied at the moment income is paid, avoiding a later reclaim. | The best-case tax outcome; clients track it in tax dashboards. |
| Restricted market | A market whose rules — foreign-ownership limits, investor registration, currency controls — constrain how easily foreign investors can hold or trade securities. | Requires market-specific messaging and workflows in your UX. |
| Safekeeping | The core custody duty of holding clients' assets securely and segregated from the custodian's own assets, so they are protected even in the custodian's insolvency. | The trust foundation every screen you ship implicitly represents. |
| Securities lending | The temporary transfer of securities to a borrower against collateral, generating fee income for the owner and enabling market activities such as short selling and settlement coverage. | Revenue product with rich data ripe for digital differentiation. |
| Segregated account | An account structure in which one client's assets are held separately and identifiably rather than pooled with other clients' assets. | A safety/transparency trade-off clients weigh; affects reporting. |
| Sub-custodian | The local agent bank a global custodian appoints in each market to hold assets at the local depository and perform local settlement and servicing. | The upstream source of most of the events your platform shows. |
| Tax reclaim | The process of recovering over-withheld tax on cross-border investment income from foreign tax authorities after payment. | Slow, paper-heavy process — prime target for digital workflow. |
| Transfer agency | The service of maintaining a fund's register of investors and processing their subscriptions, redemptions, transfers and distributions. | A separate record-keeping world your experiences must integrate. |
| Tri-party agent | A neutral third party (such as a custodian or international depository) that manages collateral selection, valuation and substitution between two trading counterparties. | Collateral products increasingly demand tri-party data views. |
| Trustee | A fiduciary appointed to hold assets and enforce the terms of a trust, fund or bond issue on behalf of beneficiaries or bondholders. | Fiduciary oversight roles impose reporting your products deliver. |
| Withholding tax | Tax deducted at source from dividends and interest paid to investors, often reduced under double-taxation treaties depending on investor domicile and type. | The reason tax status data must be right in client onboarding. |

## 2. Trade Lifecycle and Settlement

| Term | Definition | Why it matters to you |
|---|---|---|
| Affirmation | The buy-side's positive agreement to a broker's trade confirmation details, locking the trade for settlement; in the US it must now happen on trade date to support T+1. | An urgent, deadline-driven workflow to design well. |
| Allegement | A notification from a depository or custodian that a counterparty has instructed a trade against your account for which no matching instruction exists yet. | An exception state your UI must make instantly actionable. |
| Allocation | The buy-side's post-execution split of a block trade across the underlying funds or accounts it manages. | Allocation data flows determine account-level accuracy. |
| Atomic settlement | Settlement in which the exchange of asset and payment happens simultaneously and indivisibly — both legs complete or neither does — a property natively offered by distributed-ledger designs. | Vocabulary of digital-asset settlement pilots you will discuss. |
| Auto-borrow | An arrangement that automatically borrows securities to cover a pending delivery shortfall so the trade settles on time. | A fails-prevention feature clients want visibility into. |
| Back office | The operational functions that process, settle, account for and reconcile what the front office trades. | Your primary internal user base for workflow tools. |
| Best execution | The regulatory obligation on brokers and managers to obtain the most favorable overall terms reasonably available when executing client orders. | Drives demand for execution and cost analytics products. |
| Buy-in | A remedial process in which a failing seller's obligation is fulfilled by purchasing the securities in the market at the seller's cost. | The sharp end of settlement discipline; clients want warnings first. |
| CCP (central counterparty) | A clearinghouse that interposes itself between buyer and seller after a trade, becoming buyer to every seller and seller to every buyer, and manages default risk via margin. | Explains netted settlement flows and margin data in your platform. |
| Central matching | A model in which both counterparties submit trade details to a shared utility (such as DTCC's CTM) that matches them, rather than exchanging confirmations bilaterally. | The upstream utility whose output feeds your settlement status. |
| Clearing | The post-trade, pre-settlement process of confirming, matching and netting obligations and preparing them for settlement. | The stage where most status changes your UI shows are generated. |
| Confirmation | The document or message in which a broker sets out the economic details of an executed trade for the counterparty's agreement. | An input whose mismatches become the exceptions you display. |
| Continuous net settlement (CNS) | A central-counterparty system (used by DTCC's NSCC) that nets each participant's obligations in a security to a single daily position for settlement. | Explains why US street-side settlements look netted, not gross. |
| Counterparty | The other party to a trade or contract, whose failure to perform is the source of counterparty credit risk. | Counterparty data quality drives matching and risk views. |
| DvP (delivery versus payment) | A settlement mechanism in which delivery of securities occurs if and only if the corresponding cash payment occurs, eliminating principal risk. | The default safe settlement mode; a pillar term in any ops talk. |
| Fail (settlement fail) | A trade that does not settle on its intended settlement date because securities or cash were not in place. | The core exception metric your dashboards must predict and cut. |
| Fails coverage | The use of borrowed securities or credit to complete deliveries that would otherwise fail. | A custody service that turns red statuses green. |
| FoP (free of payment) | A transfer of securities without a simultaneous linked cash movement, used for portfolio transfers, collateral moves and gifts; carries principal risk. | Higher-risk instruction type needing stronger UX guardrails. |
| Front office | The revenue-generating, market-facing functions of an investment firm: portfolio management, trading, sales. | The demanding upstream users of middle-office products. |
| Give-up | An arrangement in which a trade executed with one broker is settled ("given up") to another party, commonly the client's clearing broker or prime broker. | Explains three-way settlement flows in hedge-fund servicing. |
| Gross settlement | Settlement of each trade individually, one by one, rather than on a netted basis. | Volume driver: gross markets multiply the instructions you show. |
| Hold and release | A mechanism allowing a participant to send a settlement instruction to the depository but keep it blocked ("on hold") until it is explicitly released. | A control feature power users expect in instruction screens. |
| Intended settlement date (ISD) | The date on which the parties agreed a trade should settle, against which fails and settlement-discipline penalties are measured. | The reference date behind every aging metric you display. |
| Matching | The comparison of the two counterparties' settlement instructions by a depository or utility; only matched instructions can settle. | Unmatched items are the first exception queue users check. |
| Middle office | The functions between front and back office — trade support, position management, cash and collateral management, performance and risk data. | The persona at the heart of outsourcing-driven digital demand. |
| Multilateral netting | The offsetting of obligations among many parties so each ends with a single net position per security or currency, drastically reducing settlement volumes. | Explains gaps between trade counts and settlement counts. |
| Netting | The offsetting of mutual obligations so only the net difference is settled or owed. | Fundamental to how volumes, exposure and cash needs shrink. |
| Novation | The legal substitution of one contract for another — in clearing, the replacement of the bilateral trade with two trades facing the central counterparty. | The legal magic behind CCP data structures. |
| Partial settlement | Settling a portion of a trade's quantity when the full amount is unavailable, reducing the failed remainder. | A CSDR-encouraged feature your status model must represent. |
| Place of settlement (PSET) | The depository or market where a given trade will settle, specified in the settlement instruction. | A key routing field; wrong PSET is a classic fail cause. |
| Pre-matching | Informal comparison of settlement details between custodian and counterparty before instructions are formally matched at the depository, common in emerging markets. | Manual-heavy step ripe for workflow digitization. |
| Realignment | Moving positions between accounts or depositories without change of beneficial ownership, e.g., to position securities where a delivery is due. | Background moves that explain "phantom" activity to users. |
| Recall | A lender's demand for the return of loaned securities, typically because it has sold them or wants to vote them. | Time-critical event linking lending and settlement views. |
| RvP (receive versus payment) | The receiving side of a delivery-versus-payment settlement: securities are received against simultaneous payment of cash. | The buy-side mirror of DvP in instruction data. |
| Settlement chain | The full sequence of linked deliveries through which securities move from original seller to final buyer across intermediaries. | One late link fails the chain — context for fail analytics. |
| Settlement cycle | The standard number of business days between trade date and settlement date in a market, expressed as T+n. | Market-by-market variance your products must encode. |
| Settlement discipline | Rules — most prominently the Central Securities Depositories Regulation regime in the European Union — that penalize settlement fails through cash penalties and enforce remedies. | Penalty data is now a client-facing product requirement. |
| Settlement finality | The legally defined moment after which a settlement is irrevocable and unwindable by no one, including an insolvency administrator. | The moment "pending" legitimately becomes "settled" in your UI. |
| Settlement internalization | Settling both sides of a trade on a custodian's own books when both parties are its clients, without touching the market depository. | Internalized flows need their own status representation. |
| Shaping | Splitting a large settlement instruction into several smaller ones ("shapes") to improve settlement probability and manage exposure. | Explains one order appearing as many instructions. |
| SSI (standing settlement instructions) | Pre-agreed default settlement details — accounts, depositories, cash correspondents — applied automatically to trades with a counterparty. | Bad SSIs are the top root cause of fails; a data product target. |
| STP (straight-through processing) | End-to-end automated processing of a transaction from initiation to settlement without manual touch. | The efficiency north star for every workflow you build. |
| Street side vs client side | The distinction between a trade's leg facing the market/broker (street side) and the mirroring leg on the custodian's books facing the client (client side). | Your users constantly toggle between these two views. |
| T+1 | A settlement cycle in which trades settle one business day after trade date; adopted by the United States, Canada and Mexico in May 2024, with the UK and EU targeting 2027. | The compression forcing real-time features across your roadmap. |
| Tolerance matching | Matching logic that treats two instructions as matched despite small cash differences within a defined tolerance. | Design detail that quietly eliminates thousands of exceptions. |
| Trade capture | The initial recording of an executed trade's details into processing systems. | Garbage in here becomes every downstream break you see. |
| Trade date (T) | The date a trade is executed, from which the settlement cycle is counted. | The anchor of the T+n timeline in every lifecycle view. |
| Trade enrichment | The automatic augmentation of a captured trade with reference and settlement data — instruction details, commissions, fees — needed for processing. | Enrichment failures are a silent source of downstream exceptions. |
| Turnaround trade | A same-day buy and sell of the same security, requiring the incoming receipt to fund the outgoing delivery. | Stresses intraday tracking; a classic fail scenario to visualize. |
| Unique transaction identifier (UTI) | A globally unique code identifying a single transaction across its lifecycle and across both counterparties' regulatory reports. | The joining key for cross-system transaction views. |
| Unmatched trade | A settlement instruction for which the counterparty's corresponding instruction is missing or differs. | The highest-urgency exception queue in any settlement UI. |
| Value date | The date on which a cash movement takes economic effect for interest and balance purposes. | Cash timelines in your UI hinge on value date, not entry date. |

## 3. Fund Accounting, NAV and Fund Structures

| Term | Definition | Why it matters to you |
|---|---|---|
| '40 Act fund | A US investment fund registered under the Investment Company Act of 1940 — mutual funds, exchange-traded funds and closed-end funds — subject to strict custody, governance and disclosure rules. | The regulatory wrapper of much of the US fund book you serve. |
| ABOR (accounting book of record) | The official accounting view of a fund's positions, cash and valuations used to strike the net asset value and produce financial statements. | One of the two "books" your data products must reconcile. |
| Accrual | The recognition of income or expense as it is earned or incurred — e.g., daily bond interest — rather than when cash moves. | Accrual logic explains most day-over-day NAV movement. |
| Administrator | The service provider that performs a fund's accounting, valuation, financial reporting and regulatory support. | Often State Street itself; your users sit inside this function. |
| AIF (alternative investment fund) | Under the European Union's Alternative Investment Fund Managers Directive, any collective fund that is not a UCITS retail fund — hedge funds, private equity, real estate and similar vehicles. | The alternatives segment driving fund-services growth. |
| Amortized cost | A valuation method that accretes a security's purchase discount or premium smoothly to par over its remaining life, used for short-dated money market instruments. | Explains why some money-fund prices barely move. |
| Authorized participant (AP) | A large broker-dealer permitted to create and redeem exchange-traded fund shares directly with the fund in large blocks. | A specialized, latency-sensitive user of ETF order portals. |
| Capital call | A private-markets fund's demand that investors pay in a portion of their committed capital to fund investments. | A workflow investors increasingly expect to receive digitally. |
| Carried interest | The general partner's share — classically 20% — of a private fund's profits above a hurdle, paid as performance compensation. | Core private-markets economics behind waterfall reporting. |
| Closed-end fund | A fund with a fixed number of shares that trade on an exchange at market prices, which may deviate from net asset value; investors exit by selling shares, not redeeming. | Different servicing data model from open-end funds. |
| Collective investment scheme | Any vehicle that pools money from multiple investors for management as a single portfolio under a defined structure. | The generic object all fund-servicing data describes. |
| Committed capital | The total amount investors have legally pledged to a private-markets fund, drawn down over time via capital calls. | The denominator of private-fund metrics in investor portals. |
| Creation/redemption (in-kind) | The exchange-traded fund mechanism in which authorized participants deliver or receive a basket of the underlying securities in exchange for fund shares, keeping market price near net asset value. | The engine of ETF servicing; basket data is a product surface. |
| Cut-off (dealing cut-off) | The daily deadline by which subscription and redemption orders must arrive to receive that day's fund price. | A hard deadline your order-entry UX must communicate. |
| Distribution | A payment of a fund's income or capital gains to its investors. | Investor-facing events with strict tax reporting needs. |
| Equalization | An accounting technique ensuring that investors entering a fund mid-period pay or receive fair adjustments for performance fees accrued before their entry. | Hedge-fund statement complexity your reports must explain. |
| ETF (exchange-traded fund) | An open-ended fund whose shares trade intraday on an exchange, kept close to underlying value by in-kind creation and redemption. | State Street pioneered the ETF (SPDR); a flagship client segment. |
| Expense ratio (TER) | A fund's total annual operating costs — the total expense ratio — expressed as a percentage of its assets. | Fee pressure on clients becomes fee pressure on your pricing. |
| Fair value pricing | Adjusting a security's stale or unavailable market price to a better estimate of value — e.g., after foreign markets close — using models or vendor factors. | Explains valuation overrides your data lineage must expose. |
| Feeder fund | A fund that invests substantially all its assets into a master fund, allowing different investor types or jurisdictions to access one portfolio. | Multiplies legal entities per strategy in your data model. |
| Fund of funds | A fund whose portfolio consists of holdings in other funds rather than direct securities. | Look-through reporting is a hard, valued data problem. |
| Gate | A provision limiting the percentage of a fund that can be redeemed in one dealing period, protecting remaining investors in stressed markets. | A status your investor portal must surface prominently. |
| GAV (gross asset value) | The total value of a fund's assets before deducting liabilities such as fees, expenses and borrowings. | The starting point of the NAV calculation chain you display. |
| General partner (GP) | The managing entity of a limited partnership fund, responsible for investment decisions and bearing unlimited liability. | The manager persona in private-markets servicing. |
| Hedge fund | A lightly regulated pooled vehicle for sophisticated investors that can use leverage, shorting and derivatives in pursuit of absolute returns. | A demanding client segment with bespoke data needs. |
| High-water mark | The highest net asset value a fund has previously achieved, above which performance fees may again be charged. | Performance-fee logic your statements must get right. |
| Hurdle rate | The minimum return a fund must earn before performance fees or carried interest begin to accrue. | A fee-calculation input investors scrutinize in reports. |
| IBOR (investment book of record) | A real-time or intraday view of positions and cash reflecting all known trading activity, used by the front office to know what it can trade now. | The "second book"; IBOR-ABOR gaps are a classic client pain. |
| Limited partner (LP) | An investor in a limited partnership fund whose liability is limited to its commitment and who has no management role. | The asset-owner persona of private-markets portals. |
| Management fee | The recurring fee, usually a percentage of assets or commitments, paid to a fund's manager for running the portfolio. | A standing item in the expense data you present. |
| Master–feeder | A structure in which several feeder funds consolidate their assets into one master fund that does all the investing. | Requires entity-hierarchy-aware reporting design. |
| Money market fund (MMF) | A fund investing in high-quality short-term instruments to provide daily liquidity and principal stability, used as a cash-management vehicle. | Destination of sweep balances; intraday data expectations. |
| NAV (net asset value) | The value of a fund's assets minus its liabilities; divided by shares outstanding it gives the per-share price at which investors deal. | The single most important number fund clients pay you to produce. |
| NAV error | A material mistake in a published net asset value, triggering correction, investor compensation and root-cause analysis under defined materiality thresholds. | The incident type that most damages fund-servicing trust. |
| NAV per share | The net asset value of a fund divided by its shares or units outstanding — the dealing price of an open-end fund. | The headline figure on virtually every fund screen you own. |
| Open-end fund | A fund that continuously issues and redeems shares at net asset value, growing and shrinking with investor flows. | The dominant structure behind daily NAV operations. |
| Performance fee | A fee charged as a share of a fund's gains, often subject to a hurdle rate and high-water mark. | Complex accrual clients check against your reports. |
| Pricing hierarchy | The ordered set of price sources (primary vendor, secondary vendor, broker quote, model) used to value each asset type, with rules for when to fall through to the next source. | The provenance logic your valuation transparency tools expose. |
| Redemption | An investor's withdrawal of money from a fund by selling shares back to it at net asset value. | One of the two core investor transactions your portals process. |
| Share class | A subdivision of a fund with its own fee level, currency, distribution policy or hedging, all sharing one underlying portfolio. | Multiplies the records and prices behind one fund. |
| SICAV | Société d'investissement à capital variable — a common European open-ended investment company structure, especially in Luxembourg. | A structure name you will hear constantly in EMEA fund talk. |
| Side pocket | A segregated portion of a fund holding illiquid or hard-to-value assets, in which only investors present at creation participate. | An accounting wrinkle investor statements must handle. |
| Stale price | A price that has not updated to reflect current market conditions, typically because the asset has not traded recently. | The trigger for fair-value adjustments and data-quality flags. |
| Subscription | An investor's purchase of fund shares, injecting cash into the fund at net asset value. | The other core investor transaction; onboarding-adjacent UX. |
| Swing pricing | Adjusting a fund's net asset value up or down when net flows exceed a threshold, so transacting investors bear the trading costs their flows cause. | An anti-dilution mechanism your NAV displays must footnote. |
| UCITS | Undertakings for Collective Investment in Transferable Securities — the European Union's framework for retail investment funds that can be sold across borders with a single authorization. | The passportable European fund type at the heart of EMEA servicing. |
| Umbrella fund | A single legal fund entity containing multiple ring-fenced sub-funds, each with its own portfolio and investors. | Another hierarchy layer your entity model must respect. |
| Unit trust | A fund constituted as a trust in which investors hold units and a trustee holds the assets, common in the United Kingdom and Asia. | Regional structure variety your product must not hard-code away. |
| Waterfall | The contractual order in which a private fund's proceeds are distributed among limited partners and the general partner — return of capital, preferred return, catch-up, carry. | The logic behind private-markets investor statements. |

## 4. Corporate Actions

| Term | Definition | Why it matters to you |
|---|---|---|
| Announcement capture | The sourcing, scrubbing and consolidation of corporate action event details from depositories, agents and data vendors into a single validated event record. | Upstream quality here determines your event feed's accuracy. |
| Bonus issue | A free distribution of additional shares to existing shareholders in proportion to their holdings. | A mandatory event type your notifications must classify. |
| Buyer protection | A process letting the buyer of a security trading around a voluntary event instruct its elective choice through the seller when the trade has not yet settled. | An edge-case workflow that separates good CA platforms from great. |
| Cash dividend | A distribution of a company's profits to shareholders in cash, defined by ex-date, record date and pay date. | The highest-volume event in any corporate-actions feed. |
| Consent solicitation | A request for bondholders' or shareholders' approval to amend the terms of a security or indenture, often with a fee for consenting. | A deadline-driven voluntary event needing crisp digital election. |
| Conversion | The exchange of a convertible security into the underlying shares under predefined terms. | An elective event tying fixed-income and equity data together. |
| Coupon payment | The periodic interest payment made to holders of a bond. | Bread-and-butter income event; timeliness is a client KPI. |
| Cum-/ex-dividend | Trading "cum" means the buyer acquires the right to a declared dividend; "ex" means the seller retains it. | The distinction behind market claims and entitlement disputes. |
| DRIP (dividend reinvestment plan) | An option to receive a dividend as additional shares instead of cash, often at a small discount. | A common election choice your instruction UX must support. |
| Election | A holder's instruction choosing among the options of a voluntary or choice-bearing corporate action before the deadline. | The core client action in corporate-actions digital workflow. |
| Entitlement | The quantity of cash or securities a holder is due from a corporate action, calculated from its eligible position on record date. | The number clients check first — and dispute most. |
| Ex-date | The first date on which a security trades without the right to a declared entitlement; buyers on or after ex-date do not receive it. | The pivot date of every distribution timeline you render. |
| Fractional entitlement | The non-whole share amount resulting from an event ratio, handled by rounding rules or cash-in-lieu payment. | A small detail that generates outsized client queries. |
| Golden record (corporate actions) | The single, validated version of an event's terms assembled from multiple conflicting sources, used for all downstream processing. | The data-quality concept underpinning trustworthy notifications. |
| Mandatory event | A corporate action that affects all holders automatically with no decision required, such as a stock split or cash dividend. | Straight-through candidates; no election UX needed. |
| Mandatory with choice | An event that will happen regardless, but where holders choose the form of proceeds — e.g., dividend payable in cash or stock, with a default if silent. | Requires default-handling logic and clear deadline UX. |
| Market claim | The process of redirecting an entitlement to its rightful economic owner when a trade settled after record date but was dealt cum-entitlement. | Automated claims reduce a notorious source of client friction. |
| Merger (event) | A corporate action in which one company's shares are exchanged for cash, shares of another company, or a mix, per the deal terms. | High-value, high-attention events that must render clearly. |
| MT564 | The ISO 15022 SWIFT message type for corporate action notifications: announcing an event, its terms, options and deadlines to account holders. | The wire format behind your event notifications. |
| MT565 | The ISO 15022 SWIFT message type by which a holder sends its corporate action election instruction to its custodian. | The message your election screens ultimately generate. |
| MT566 | The ISO 15022 SWIFT message type confirming the outcome of a corporate action — the cash and/or securities actually credited or debited. | The confirmation data your posting views display. |
| MT567 | The ISO 15022 SWIFT message type reporting the status (accepted, rejected, pending) of a corporate action instruction. | Feeds the instruction-status tracker clients refresh anxiously. |
| MT568 | The ISO 15022 SWIFT message type carrying corporate action narrative — free-text details that do not fit structured fields. | The unstructured tail your parsing and AI tooling must tame. |
| Odd-lot offer | An offer allowing holders of less than a standard trading lot to sell or round up their position without normal dealing costs. | A niche voluntary event your taxonomy must still cover. |
| Oversubscription | An election to take up more than one's pro-rata entitlement in a rights or similar offer, filled if other holders decline theirs. | An optional field in election UX that clients value. |
| Pay date | The date on which a corporate action's cash or securities proceeds are actually distributed to entitled holders. | The date clients watch; late pay date equals support tickets. |
| Proration | The scaling down of accepted instructions when a voluntary offer is oversubscribed, so each participant is filled proportionally. | Explains partial outcomes your results screens must explain. |
| Protect instruction | A mechanism letting a buyer whose trade has not settled preserve its right to participate in an expiring voluntary offer. | A deadline edge case power users expect you to handle. |
| Proxy event (AGM/EGM) | A shareholder meeting — annual or extraordinary general meeting — for which holders receive agendas and lodge votes through the custody chain. | Governance workflow increasingly delivered digitally end-to-end. |
| Record date | The date on which an issuer takes a snapshot of registered holders to determine who is entitled to an announced distribution or vote. | The entitlement snapshot behind every calculated position. |
| Reverse split | The consolidation of shares — e.g., ten old shares become one new share — reducing share count and raising the per-share price. | A mandatory event with fractional-share consequences. |
| Rights issue | An offer of new shares to existing shareholders in proportion to their holdings, usually at a discount, via tradable or non-tradable rights. | A complex voluntary event that stress-tests election UX. |
| Scheme of arrangement | A court-approved procedure (common in UK/Commonwealth markets) for effecting takeovers or restructurings binding on all shareholders. | An event type with distinctive timeline and terminology. |
| Scrip dividend | A dividend paid in newly issued shares rather than cash, sometimes at the holder's choice. | Another cash-or-stock election pattern to support. |
| Spin-off | The distribution of shares in a subsidiary to the parent company's shareholders, creating a separate listed company. | Creates new positions from nowhere — a data-model test. |
| SRD II (Shareholder Rights Directive II) | The European Union directive requiring intermediaries to transmit shareholder identification, meeting information and votes quickly through the custody chain. | Regulatory driver of real-time proxy and disclosure features. |
| Stock split | The division of existing shares into a larger number — e.g., one share becomes ten — with no change in total value. | High-visibility mandatory event; position math must be flawless. |
| Tender offer | A public offer to purchase some or all of a security from holders at a stated price for a limited period. | A high-stakes voluntary event with hard deadlines to surface. |
| Transformation | The automatic conversion of pending settlement instructions into instructions for the new security or cash when a corporate action restructures the original security mid-settlement. | Post-event cleanup your status views must narrate clearly. |
| Voluntary event | A corporate action in which each holder decides whether and how to participate, such as a tender offer or rights issue. | The event class that drives your election workflow product. |

## 5. Payments, SWIFT and Cash

| Term | Definition | Why it matters to you |
|---|---|---|
| ACH (Automated Clearing House) | The US batch-based network for low-value electronic payments such as payroll and vendor payments, settling in cycles rather than in real time. | Contrast case for the wire flows your clients mostly use. |
| Available balance | The portion of a cash balance a client can actually use now, after holds, pending debits and credit arrangements are considered. | The balance figure users act on; must be defined precisely in UX. |
| Back-valuation | Applying an earlier value date to a late-processed cash entry so the client is not disadvantaged on interest. | An adjustment your cash statements must display intelligibly. |
| BIC (Business Identifier Code) | The ISO 9362 code (often called a SWIFT code) identifying a financial institution — and optionally a branch — in financial messaging. | The addressing key of every SWIFT flow you visualize. |
| camt.053 | The ISO 20022 end-of-day bank-to-customer account statement message, the modern successor to the MT940 statement. | The statement feed powering next-gen cash reporting. |
| camt.054 | The ISO 20022 bank-to-customer debit/credit notification message reporting individual entries as they post. | The event feed behind real-time cash activity screens. |
| Cash ladder | A time-bucketed view of projected cash inflows and outflows per account and currency, showing expected balances into the future. | A flagship treasury visualization your clients rely on daily. |
| Cash projection | The forecast of an account's future balance based on known settlements, income, corporate actions and standing movements. | Prediction quality here is a genuine digital differentiator. |
| CHAPS | The United Kingdom's sterling real-time gross settlement system for high-value same-day payments. | UK cash leg of your clients' settlement activity. |
| CHIPS (Clearing House Interbank Payments System) | A private US high-value payment system that nets large-dollar payments among major banks, complementing Fedwire. | Explains routing variety in US dollar cash movements. |
| CLS (Continuous Linked Settlement) | The industry utility that settles both legs of foreign-exchange trades simultaneously (payment versus payment), eliminating cross-currency settlement risk. | Context for FX settlement status in multicurrency views. |
| Correspondent banking | The provision of accounts and payment services by one bank to another, enabling banks to move money in currencies and markets where they lack presence. | The network behind every cross-border cash movement you show. |
| Cover payment | A payment structure in which the instruction to the beneficiary's bank travels directly while the funds move separately through correspondents (classically an MT103 with an MT202 COV cover). | Explains why message receipt and funds arrival can diverge. |
| Cut-off time | The deadline, per currency and payment type, after which an instruction will be processed the next business day. | Deadline logic your payment UX must make impossible to miss. |
| FedNow | The US Federal Reserve's instant payment service, settling individual payments in seconds around the clock. | Signals the 24/7 expectations migrating into institutional cash. |
| Fedwire | The US Federal Reserve's real-time gross settlement system for high-value US dollar payments. | The final settlement rail for the dollar legs you display. |
| Herstatt risk | Foreign-exchange settlement risk: paying away one currency before receiving the other, named after a 1974 bank failure that crystallized it. | The classic risk story behind payment-versus-payment design. |
| IBAN (International Bank Account Number) | A standardized international account identifier encoding country, bank and account, used to route cross-border payments accurately. | Validation of IBANs is table stakes in payment input UX. |
| Intraday liquidity | The funding available to meet payment obligations during the business day, as opposed to end-of-day balances. | Regulators and treasurers now demand intraday views you build. |
| ISO 20022 | The international standard for financial messaging based on rich, structured XML data models, replacing legacy formats across payments and securities. | The data-rich standard powering your next-generation feeds. |
| MT vs MX | Shorthand for the migration from legacy SWIFT MT messages (ISO 15022 and earlier, terse tagged text) to MX messages (ISO 20022, structured XML). | A multi-year translation problem your platforms sit astride. |
| MT103 | The legacy SWIFT message for a single customer credit transfer — the classic cross-border wire. | Still ubiquitous; your payment tracking must parse it. |
| MT202 / MT202 COV | The legacy SWIFT messages for bank-to-bank transfers; the COV variant carries underlying customer details when covering a customer payment. | The interbank leg behind client payments you trace. |
| MT535 | The ISO 15022 SWIFT statement of holdings message reporting securities positions in an account. | A core position feed institutional clients still consume. |
| MT540–MT548 | The ISO 15022 SWIFT settlement message family: instructions to receive or deliver free or against payment (540–543), confirmations (544–547) and status advices (548). | The message backbone of the settlement statuses you display. |
| Nostro | An account a bank holds with another bank in that bank's currency ("our account with you"), used to settle payments in that currency. | Nostro reconciliation quality shapes your cash data accuracy. |
| Overdraft | A negative cash balance in an account, representing credit extended by the account-holding bank, often priced and limit-controlled. | Overdraft alerts and analytics are valued treasury features. |
| pacs.002 | The ISO 20022 payment status report message, confirming or rejecting a payment instruction between financial institutions. | The status heartbeat of ISO-native payment tracking. |
| pacs.008 | The ISO 20022 customer credit transfer message between financial institutions — the modern successor to the MT103 wire. | The flagship ISO 20022 payment message in your data flows. |
| pacs.009 | The ISO 20022 financial-institution-to-financial-institution credit transfer — the interbank funding leg, successor to the MT202. | Completes the picture when tracing cover payments. |
| pain.001 | The ISO 20022 customer-to-bank payment initiation message by which a corporate or fund instructs its bank to pay. | The instruction format your payment-initiation APIs speak. |
| Payment repair | The manual or automated correction of a payment whose routing or beneficiary data is incomplete or invalid before it can process. | Repair rates are an STP metric your tooling can improve. |
| RTGS (real-time gross settlement) | A payment system that settles each transfer individually and irrevocably in central bank money in real time. | The gold-standard rail concept behind Fedwire, CHAPS, TARGET. |
| RTP (Real-Time Payments) | The Clearing House's US instant payment network, settling continuously with immediate finality. | Another 24/7 rail shaping client expectations of "instant." |
| SEPA (Single Euro Payments Area) | The European framework making euro credit transfers and direct debits uniform across member countries. | The scheme context for euro cash movements you present. |
| SWIFT | The Society for Worldwide Interbank Financial Telecommunication — the cooperative operating the secure messaging network that connects over 11,000 financial institutions. | The nervous system of custody; most of your data arrives on it. |
| SWIFT gpi | SWIFT's global payments innovation service, adding end-to-end tracking, confirmation and speed standards to cross-border payments via a unique tracking reference. | The tracking data behind "where is my payment?" features. |
| Sweep | An automated end-of-day (or intraday) transfer moving balances between accounts to a target level or investment vehicle. | Configurable sweeps are a self-service feature clients want. |
| T2S (TARGET2-Securities) | The Eurosystem's single platform settling securities against central bank money across most European markets on one technical system. | Harmonized European settlement data source for your platform. |
| TARGET2/T2 | The Eurosystem's real-time gross settlement system for euro payments in central bank money. | The euro cash rail beneath European settlement flows. |
| UETR (unique end-to-end transaction reference) | A universally unique identifier carried by a payment across every bank in its chain, enabling end-to-end tracking. | The key that powers payment-tracking UX across banks. |
| Value dating | The assignment of the date on which a cash entry earns or costs interest and affects the usable balance. | Subtle date logic that must be consistent across your screens. |
| Vostro | An account a bank holds on behalf of a foreign bank in the domestic currency ("your account with us") — the mirror of a nostro. | Completes the correspondent picture in cash data models. |
| Wire transfer | A real-time or same-day electronic transfer of funds between banks, typically high-value and irrevocable once settled. | The workhorse cash movement your payment screens track. |

## 6. Markets, Instruments and Reference Data

| Term | Definition | Why it matters to you |
|---|---|---|
| ABS (asset-backed security) | A bond backed by a pool of receivables such as auto loans or credit card balances, whose cash flows pay investors. | Structured assets stress pricing and analytics displays. |
| ADR (American depositary receipt) | A US-listed certificate representing shares of a foreign company held by a depositary bank, letting US investors trade foreign stocks in dollars. | A wrapper whose fees and events differ from ordinary shares. |
| Basis point (bp) | One hundredth of one percent (0.01%); the standard unit for quoting fees, spreads and rate moves. | The unit of custody pricing and every fee conversation. |
| Benchmark (index) | A standard portfolio or rate against which investment performance or pricing is measured, such as the S&P 500 or SOFR. | Benchmark-relative analytics are core client reporting. |
| Bond | A debt security obligating the issuer to pay periodic interest and repay principal at maturity. | Fixed income dominates custody books; know its anatomy. |
| Callable bond | A bond the issuer may redeem before maturity at predefined dates and prices. | Optionality complicates the income projections you show. |
| CDS (credit default swap) | A derivative in which one party pays a premium for protection against a reference entity's default. | OTC derivative type appearing in risk and collateral views. |
| Commercial paper | Short-term unsecured corporate debt, typically maturing within 270 days, used for working-capital funding. | A money-market staple in cash-management portfolios. |
| Convertible bond | A bond that the holder can convert into a predefined number of the issuer's shares. | Hybrid instrument bridging debt and equity data models. |
| Corporate hierarchy (entity data) | Reference data linking legal entities to their parents, subsidiaries and ultimate owners. | Powers exposure roll-ups and know-your-customer views. |
| CUSIP | The nine-character identifier for North American securities issued by the CUSIP Services Bureau. | One of several identifiers your symbology layer must map. |
| Derivative | A contract whose value derives from an underlying asset, rate or index — futures, options, swaps, forwards. | Derivatives servicing data differs radically from securities. |
| Digital asset custody | The safekeeping of cryptographic assets by controlling their private keys within institutional-grade security and governance. | A frontier State Street is building; new UX paradigms needed. |
| Duration | A measure of a bond's price sensitivity to interest-rate changes, expressed in years. | A standard risk statistic clients expect beside positions. |
| Equity | An ownership share in a company, carrying rights to dividends, votes and residual value. | Half the custody book; its lifecycle drives your event volume. |
| ETD (exchange-traded derivative) | A standardized derivative — future or listed option — traded on an exchange and cleared through a central counterparty. | Margin and position data flows differ from OTC contracts. |
| €STR (euro short-term rate) | The euro area's overnight risk-free reference rate, reflecting banks' wholesale unsecured borrowing costs. | Euro benchmark in cash, collateral and pricing data. |
| FIGI (Financial Instrument Global Identifier) | An open, free instrument identifier maintained by Bloomberg as an alternative to proprietary codes. | An option in the identifier-mapping strategy of your data layer. |
| Fixed income | The asset class of debt instruments paying defined interest — government, corporate, securitized and municipal bonds. | Pricing opacity here drives valuation-transparency demand. |
| Forward | A privately negotiated contract to buy or sell an asset at a set price on a future date. | The simplest OTC derivative appearing in FX and hedging data. |
| Futures | Standardized exchange-traded contracts to buy or sell an asset at a set price on a future date, marked to market daily with margin. | Daily margin flows feed the cash movements you display. |
| FX forward | A contract to exchange two currencies at a fixed rate on a future date, used for hedging currency exposure. | Ubiquitous in hedged share classes and portfolio hedging. |
| FX swap | The combination of a spot currency exchange and an offsetting forward, used to roll liquidity across currencies. | A funding tool visible in clients' cash and FX activity. |
| Golden copy | The certified master version of a reference-data record — instrument, entity, price — that all systems should consume. | The prerequisite for consistency across your product suite. |
| Government bond | Debt issued by a sovereign — Treasuries, gilts, Bunds — usually the benchmark risk-free assets of a currency. | The collateral and liquidity backbone of clients' portfolios. |
| Index | A rules-based calculation representing the value of a defined basket of securities, used for benchmarking and product construction. | Index data licensing shapes what analytics you can display. |
| Interest rate swap (IRS) | A derivative exchanging fixed-rate interest payments for floating-rate payments on a notional amount. | The most common OTC derivative in servicing data. |
| ISIN (International Securities Identification Number) | The twelve-character ISO 6166 global identifier for a security. | The primary key of instrument data across your estate. |
| LEI (Legal Entity Identifier) | The twenty-character ISO 17442 code uniquely identifying legal entities in financial transactions worldwide. | The entity key regulators require and your data should join on. |
| Liquidity (market) | The ease of buying or selling an asset quickly without materially moving its price. | Liquidity tiering drives pricing quality flags in your data. |
| Market data | Real-time and historical prices, quotes, rates and analytics licensed from exchanges and vendors. | Licensing costs and entitlements constrain your product design. |
| Market maker | A firm quoting continuous buy and sell prices in a security, profiting from the spread while providing liquidity. | Context for ETF liquidity and pricing conversations. |
| MBS (mortgage-backed security) | A bond backed by pooled mortgage payments, with prepayment behavior that complicates its cash flows. | Amortizing, factor-based instruments test position math. |
| Money market instrument | A short-term, high-quality debt instrument — treasury bill, commercial paper, certificate of deposit — maturing typically within a year. | The raw material of cash and sweep products you support. |
| Municipal bond | Debt issued by US state and local governments, often carrying tax advantages for US investors. | A US-specific asset class with unique data conventions. |
| Option | A contract giving the right, but not the obligation, to buy (call) or sell (put) an asset at a set price by a set date. | Options positions carry exercise events your platform tracks. |
| OTC (over the counter) | Trading conducted bilaterally between parties rather than on an exchange. | OTC assets need bespoke valuation and confirmation data. |
| Par value | The face amount of a bond repaid at maturity, against which its price is quoted as a percentage. | Explains bond quantities and prices in position screens. |
| Preferred stock | Equity ranking ahead of common shares for dividends and liquidation, usually with fixed dividends and limited voting rights. | A hybrid class with its own event and income patterns. |
| Primary market | The market in which securities are first issued and sold to investors, as opposed to subsequent trading. | New-issue flows create the positions your systems inherit. |
| Private equity (asset class) | Ownership stakes in companies not listed on public exchanges, held through funds with long lock-ups. | The illiquid asset class driving alternatives-servicing growth. |
| Repo (repurchase agreement) | The sale of securities with a binding agreement to repurchase them at a set price on a set date — economically a collateralized loan. | Financing activity entwined with collateral views you build. |
| Reverse repo | The mirror of a repurchase agreement: buying securities with an agreement to resell, i.e., lending cash against collateral. | The cash-investing side of the same financing data. |
| Secondary market | The market where already-issued securities trade among investors. | The source of the daily trade flow your lifecycle tools track. |
| Securities master | The central database of instrument reference data — identifiers, terms, classifications — feeding all processing systems. | Every mismatch here becomes a defect in your product. |
| SEDOL | The seven-character security identifier issued by the London Stock Exchange, common in UK and Irish data. | Another symbology your identifier mapping must cover. |
| SOFR (Secured Overnight Financing Rate) | The US dollar risk-free reference rate based on overnight Treasury repurchase transactions, successor to dollar LIBOR. | The dollar benchmark embedded across rates data you show. |
| SONIA (Sterling Overnight Index Average) | The sterling overnight risk-free rate administered by the Bank of England. | The sterling benchmark in cash and derivatives data. |
| Spread | The difference between two prices or yields — bid versus ask, or a bond's yield over the risk-free curve. | A compact risk/cost signal used across analytics screens. |
| Stablecoin | A digital token designed to hold a stable value against a reference asset, typically the US dollar, backed by reserves. | A candidate settlement asset in digital-cash initiatives. |
| Structured product | A packaged investment combining derivatives with bonds or deposits to deliver a customized payoff profile. | Hard-to-price holdings that strain valuation transparency. |
| Swap | A derivative in which two parties exchange streams of cash flows — fixed for floating rates, currencies or returns — over time. | The generic OTC family your derivatives data must model. |
| Symbology | The mapping and cross-referencing of the many identifier schemes (ISIN, CUSIP, SEDOL, ticker, FIGI) that name the same instrument. | The unglamorous capability that makes cross-source data join. |
| Ticker | The short exchange trading symbol for a listed security. | The identifier users type first in any search box you build. |
| Tokenized asset | A traditional asset represented as a digital token on a distributed ledger, enabling programmable transfer and fractional ownership. | The asset form factor of custody's next decade. |
| Total return swap | A derivative exchanging the total economic return of an asset (income plus price change) for a financing rate. | Gives synthetic exposure that complicates holdings views. |
| Volatility | The degree of variation in an asset's price over time, a core input to risk measures and option pricing. | A standard statistic in the risk analytics you surface. |
| Yield | The income return of an investment expressed as an annual percentage of its price. | The lens through which fixed-income clients read your screens. |
| Yield curve | The plot of yields across maturities for comparable debt, describing the term structure of interest rates. | A canonical visualization in any rates or portfolio view. |
| Zero-coupon bond | A bond paying no periodic interest, issued at a discount and redeemed at face value. | Edge case for income accrual logic in accounting data. |

## 7. Regulation, Risk and Compliance

| Term | Definition | Why it matters to you |
|---|---|---|
| AIFMD (Alternative Investment Fund Managers Directive) | The European Union directive regulating managers of non-retail funds, imposing depositary, reporting and remuneration requirements. | Source of depositary oversight duties your reporting supports. |
| AML (anti-money laundering) | The body of laws and controls requiring financial institutions to detect, prevent and report the laundering of criminal proceeds. | Constraints and checks baked into every onboarding flow you own. |
| Basel III | The international framework of bank capital, leverage and liquidity standards agreed after the 2008 crisis by the Basel Committee on Banking Supervision. | Shapes the balance-sheet costs behind deposit and credit pricing. |
| BCBS 239 | The Basel Committee's principles for risk data aggregation and risk reporting, requiring banks to produce accurate, complete, timely risk data. | The regulatory backbone of your data lineage and quality work. |
| CASS (Client Assets Sourcebook) | The UK Financial Conduct Authority's rules for protecting client money and assets, including segregation and reconciliation duties. | Governs how client asset data must be controlled and evidenced. |
| CCAR (Comprehensive Capital Analysis and Review) | The Federal Reserve's annual capital planning and stress-testing exercise for large US banks. | A recurring corporate event that redirects budgets and attention. |
| CDD/EDD (customer/enhanced due diligence) | The know-your-customer processes of verifying who a client is; enhanced due diligence applies deeper scrutiny to higher-risk clients. | Determines the evidence your onboarding journeys must collect. |
| Chinese wall (information barrier) | Controls separating parts of a firm so confidential information from one business cannot improperly reach another. | Constrains data sharing and entitlement design across products. |
| Compliance monitoring and testing | The second-line program that checks, on a risk-based schedule, whether the business actually follows regulatory obligations and policies. | Your products will be tested; design for evidence from day one. |
| Conduct risk | The risk of poor outcomes for clients or markets arising from a firm's behavior, culture or product design. | Poorly designed digital journeys can themselves create it. |
| Consent order | A formal, public settlement with a regulator obligating a firm to remediate specified failures under supervision. | The scenario that turns remediation into your top roadmap item. |
| CSDR (Central Securities Depositories Regulation) | The European Union regulation governing central securities depositories and imposing the settlement discipline regime of cash penalties for fails. | Penalty transparency is now a client-facing product need. |
| Dodd-Frank Act | The sweeping 2010 US financial reform law covering systemic risk oversight, derivatives clearing, the Volcker Rule and consumer protection. | The statutory backdrop of much US market structure you serve. |
| DORA (Digital Operational Resilience Act) | The European Union regulation requiring financial firms to manage information-technology risk, test resilience, report incidents and control third-party technology providers. | Directly regulates the platforms and vendors you build with. |
| EMIR (European Market Infrastructure Regulation) | The European Union regulation requiring derivatives reporting to trade repositories, central clearing of standard contracts, and risk mitigation for the rest. | Source of derivative reporting flows and margin requirements. |
| ERISA (Employee Retirement Income Security Act) | The 1974 US law setting fiduciary and prudence standards for private pension plans and their service providers. | Governs duties owed to a core US asset-owner client base. |
| FCA (Financial Conduct Authority) | The United Kingdom's conduct regulator for financial services firms and markets. | A key regulator of the UK entities your products serve. |
| FinCEN (Financial Crimes Enforcement Network) | The US Treasury bureau administering anti-money-laundering law, collecting suspicious activity reports and setting related rules. | Endpoint of the monitoring your flows must support. |
| FINRA (Financial Industry Regulatory Authority) | The self-regulatory organization overseeing US broker-dealers and their conduct. | Regulates the broker counterparties in your trade flows. |
| GDPR (General Data Protection Regulation) | The European Union's data-privacy law governing collection, processing and transfer of personal data, with heavy penalties. | Shapes analytics, tracking and personalization you can ship. |
| G-SIB (global systemically important bank) | A bank designated by the Financial Stability Board as systemically important globally, attracting capital surcharges and stricter supervision; State Street is one. | Explains the compliance intensity around everything you do. |
| Horizon scanning | The systematic tracking of upcoming regulatory changes to prepare the business in time. | Feeds your roadmap with non-negotiable regulatory dates. |
| Inherent risk | The level of risk in an activity before considering any controls that mitigate it. | The "before" picture in every risk assessment you join. |
| Internal audit | The third line of defense: an independent function assuring the board that risk management and controls actually work. | Will audit your product processes; keep decisions documented. |
| Issue management | The formal process of recording control weaknesses or failures, assigning remediation owners and tracking closure. | Product gaps become "issues" with dated commitments you own. |
| KRI (key risk indicator) | A metric monitored to signal rising risk exposure — e.g., reconciliation break aging or failed-trade rates — with thresholds that trigger action. | Your dashboards often are the KRI delivery mechanism. |
| KYC (know your customer) | The regulatory requirement to identify and verify clients and understand their expected activity before and during a relationship. | The compliance core of client onboarding experiences. |
| LCR (liquidity coverage ratio) | The Basel III requirement that banks hold enough high-quality liquid assets to survive a thirty-day stress outflow scenario. | Why deposits and intraday credit carry balance-sheet costs. |
| MiFID II (Markets in Financial Instruments Directive II) | The European Union's market-conduct framework covering trading transparency, best execution, research unbundling and investor protection. | Source of execution and cost-disclosure data clients need. |
| Model risk management (SR 11-7) | The governance of models — validation, documentation, performance monitoring — per Federal Reserve guidance SR 11-7, now extended to artificial-intelligence models. | The approval gate every AI feature you propose must pass. |
| MRA (matter requiring attention) | A formal supervisory finding by a US banking regulator requiring corrective action, short of an enforcement action. | An MRA can freeze discretionary roadmap in favor of fixes. |
| NIST CSF (Cybersecurity Framework) | The US National Institute of Standards and Technology's framework organizing cybersecurity into functions — govern, identify, protect, detect, respond, recover. | Common language of the security reviews your products face. |
| NYDFS Part 500 | The New York Department of Financial Services cybersecurity regulation mandating programs, controls, testing and incident notification for covered financial firms. | A binding cyber baseline for New York-chartered operations. |
| OCC (Office of the Comptroller of the Currency) | The US regulator chartering and supervising national banks and federal branches. | A primary prudential supervisor whose exams touch your work. |
| OFAC (Office of Foreign Assets Control) | The US Treasury office administering economic sanctions programs; transactions touching sanctioned parties or countries are prohibited. | The reason payment and settlement flows pass screening gates. |
| Operational resilience | The ability to prevent, adapt to, respond to and recover from disruptions while continuing to deliver important business services within set impact tolerances. | Your client-facing platforms are designated important services. |
| Operational risk | The risk of loss from failed processes, people, systems or external events — the dominant risk type in custody and asset servicing. | The risk category your automation directly reduces. |
| Penetration testing | Authorized simulated attacks on systems to find exploitable vulnerabilities before adversaries do. | A gate before your releases touch the internet. |
| PII (personally identifiable information) | Data that can identify an individual — names, identifiers, contact details — subject to privacy law and strict handling controls. | Determines what your analytics and logs may capture. |
| RCSA (risk and control self-assessment) | The structured periodic exercise in which each business identifies its risks, maps its controls and rates residual exposure. | You will own RCSA entries for your product processes. |
| Recovery and resolution planning | The "living wills" describing how a systemically important bank could be stabilized or wound down without taxpayer rescue. | Context for entity-structure constraints on your platforms. |
| Regulatory reporting | The production and submission of mandated data returns to supervisors — capital, liquidity, transactions, holdings. | A data product discipline; errors here are reportable events. |
| Residual risk | The risk remaining after controls are applied to inherent risk. | The number risk committees actually debate. |
| Risk appetite | The amount and type of risk an organization is willing to accept in pursuit of its objectives, set by the board and cascaded as limits. | Frames how bold your product bets are allowed to be. |
| SEC (Securities and Exchange Commission) | The US regulator of securities markets, public companies, funds and investment advisers. | Its rulemaking (e.g., T+1) regularly rewrites your roadmap. |
| SEC Rules 17f-5/17f-7 | US rules governing how registered funds may hold assets with foreign custodians and depositories, requiring risk analysis of each arrangement. | The compliance backbone of global custody network data. |
| Sanctions screening | The automated checking of payments, trades and parties against sanctions lists before processing. | A latency and false-positive factor in your payment UX. |
| Segregation of duties | The control principle that no single person should both execute and approve a sensitive action. | Drives maker-checker workflow patterns in your designs. |
| SOC 1 / SOC 2 | Independent auditor reports on a service organization's controls — SOC 1 for financial-reporting controls, SOC 2 for security, availability, integrity, confidentiality and privacy. | Clients' auditors read these before trusting your platform. |
| SOX (Sarbanes-Oxley Act) | The 2002 US law requiring management certification of financial reports and effective internal control over financial reporting. | Change controls on in-scope systems constrain release process. |
| Stress testing | Evaluating how portfolios, capital or operations would perform under severe but plausible adverse scenarios. | A data-hungry exercise your analytics products can serve. |
| Three lines of defense | The governance model dividing responsibility among the business that owns risk (first line), risk and compliance functions that oversee it (second line), and internal audit that assures it (third line). | Tells you who must approve, challenge and audit your work. |
| Travel rule | The requirement that originator and beneficiary information "travel" with funds transfers (and increasingly crypto transfers) through the payment chain. | A data-completeness rule embedded in payment products. |
| Volcker Rule | The Dodd-Frank provision restricting banks from proprietary trading and certain fund investments. | Boundary condition on what a custodian bank may do. |
| Whistleblower program | Protected channels through which employees can report suspected wrongdoing, with anti-retaliation safeguards. | A cultural fixture; your teams must know it exists. |

## 8. Product Management and UX

| Term | Definition | Why it matters to you |
|---|---|---|
| A/B testing | Comparing two variants of an experience with randomized user groups to measure which performs better on a defined metric. | Harder in B2B enterprise UX, but still your evidence engine. |
| Accessibility (WCAG) | Designing products usable by people with disabilities, measured against the Web Content Accessibility Guidelines. | A legal and contractual requirement for institutional portals. |
| Activation | The moment a new user first experiences a product's core value, and the metric tracking how many get there. | Onboarding-to-value speed is your stickiest growth lever. |
| Adoption | The extent to which target users actually use a capability after it ships, measured by breadth and depth of usage. | The metric that separates shipped from successful. |
| Agile | An iterative delivery philosophy favoring small increments, continuous feedback and adaptive planning over big up-front plans. | The operating rhythm of your engineering partners. |
| Backlog | The ordered list of work items — features, fixes, debt — awaiting a team's attention, ranked by value. | Your prioritization decisions live and die here. |
| Beta | A pre-general-availability release to a limited audience to validate quality and value under real conditions. | The controlled way to learn with risk-averse bank clients. |
| Churn | The loss of customers or users over a period, the inverse of retention. | In custody it shows up as mandate loss — slow but brutal. |
| Client advisory board | A standing group of key clients convened regularly to review direction, priorities and prototypes. | Your best structural defense against building the wrong thing. |
| CSAT (customer satisfaction score) | A survey metric asking users to rate satisfaction with a product or interaction, typically on a 1–5 scale. | A journey-level pulse to pair with NPS's relationship view. |
| Customer journey map | A visualization of the end-to-end steps, touchpoints, emotions and pain points a customer experiences to accomplish a goal. | Exposes the cross-silo handoffs that ruin client experience. |
| Design system | A shared library of reusable components, patterns and standards that keeps product experiences consistent and speeds delivery. | Your force multiplier for coherence across a big portfolio. |
| Design tokens | Named design decisions — colors, spacing, typography — stored as data so they apply consistently across platforms and themes. | The plumbing that makes rebrands and dark mode cheap. |
| Discovery | The continuous work of understanding problems, users and constraints — through research, data and prototypes — before committing to build. | The habit that protects your roadmap from confident guesses. |
| Dual-track agile | Running discovery and delivery as parallel continuous tracks, with discovery feeding validated items into delivery. | The operating model for balancing learning and shipping. |
| Epic | A large body of work that delivers a significant outcome and is broken down into smaller stories for delivery. | The unit of roadmap-to-backlog translation. |
| Feature parity | Matching the capabilities of an existing product (often a legacy system being replaced) in its successor. | The trap of modernization programs — parity is not the goal. |
| GTM (go-to-market) | The coordinated plan for launching a product: positioning, pricing, sales enablement, marketing, support readiness and rollout. | Shipping is half the job; GTM is how value reaches clients. |
| Heuristic evaluation | An expert review of an interface against established usability principles to find problems quickly and cheaply. | A fast quality gate when full research is not feasible. |
| Information architecture | The structural organization and labeling of content and navigation so users can find and understand what they need. | Dense financial data lives or dies by its architecture. |
| JTBD (jobs to be done) | A framing that defines products by the job a customer hires them to do — the progress sought in a circumstance — rather than by features or demographics. | Cuts through feature requests to the underlying client need. |
| Kanban | A flow-based delivery method visualizing work on a board with limits on work in progress to expose bottlenecks. | Fits operations-adjacent teams with continuous intake. |
| Kano model | A framework classifying features as basic expectations, performance factors or delighters based on their effect on satisfaction. | Explains why table-stakes work never wins praise but must ship. |
| MVP (minimum viable product) | The smallest version of a product that lets you test its core value hypothesis with real users. | In banking, "viable" includes compliant, secure and supported. |
| North star metric | The single metric that best captures the value a product delivers to customers, used to align teams over the long term. | Your instrument for steering a portfolio without micromanaging. |
| NPS (net promoter score) | A loyalty metric derived from asking how likely customers are to recommend you, calculated as promoters minus detractors. | The relationship-level score your executives will quote. |
| OKR (objectives and key results) | A goal-setting method pairing a qualitative objective with a few measurable key results that define success. | The alignment language of most modern product organizations. |
| Onboarding (client) | The end-to-end process of taking a new client live — legal, compliance, account setup, connectivity, training. | In custody it can take months; a prime digitization target. |
| Outcome over output | The principle of measuring success by change in customer or business results, not by volume of features shipped. | The cultural shift your metrics and reviews must reinforce. |
| Persona | An evidence-based archetype of a user group — their goals, context and pain points — used to keep design grounded. | Custody has sharply distinct personas; design for each. |
| Pilot | A limited production deployment with one or a few clients to validate value and operability before broad rollout. | The standard de-risking pattern for enterprise features. |
| Platform product | A product whose users are other builders — internal teams or clients consuming APIs and services to compose their own solutions. | Your API channel is a product, not an integration afterthought. |
| PRD (product requirements document) | The document defining a product or feature's purpose, users, requirements, constraints and success measures. | Your instrument for aligning engineering, risk and ops. |
| Pricing and packaging | The design of what is bundled, tiered and charged for — the commercial architecture of a product. | Digital capabilities increasingly anchor custody deals. |
| Product analytics | Instrumented measurement of in-product behavior — funnels, retention, feature usage — to inform decisions. | You cannot manage a portal you do not measure. |
| Product–market fit | The state in which a product satisfies strong demand from a well-defined market, evidenced by pull rather than push. | The bar for new ventures before scaling investment. |
| Product ops | The function that runs the product organization's tooling, data, processes and rituals so product managers can focus on decisions. | Scales consistency across your growing product group. |
| Prototype | A quickly built, often non-functional representation of a design used to test ideas before engineering investment. | Cheapest way to be wrong; use before every big build. |
| Retention | The share of users or customers who continue using a product over time, often shown as cohort curves. | The truest signal of delivered value in your portal metrics. |
| RICE | A prioritization score computed from reach, impact, confidence and effort, used to compare initiatives. | A defensible way to rank a contested backlog. |
| Roadmap | A communicated plan of intended product direction over time, ideally organized around outcomes and themes rather than dated feature lists. | Your most-read artifact; manage it as a promise ledger. |
| Scrum | An agile framework organizing work into fixed-length sprints with defined roles (product owner, scrum master) and ceremonies. | The delivery cadence most of your squads will run. |
| Segmentation | Dividing customers into groups with distinct needs and economics so products and service models can be targeted. | Asset owners, managers and insurers need different experiences. |
| Service blueprint | A diagram linking the customer journey to the front-stage staff actions, back-stage processes and systems that support each step. | Essential where your "product" is part software, part operations. |
| Stakeholder map | An analysis of the people affected by or influential over an initiative, with their interests and required engagement. | Bank initiatives fail on stakeholders more than on technology. |
| Story point | A relative, unitless estimate of a work item's size used by agile teams for planning. | Useful for team planning; dangerous as a productivity metric. |
| Sunset | The managed retirement of a product or feature, including client migration, contractual notice and decommissioning. | Portfolio hygiene; every legacy screen you kill funds the future. |
| Time to value | The elapsed time from a client's commitment (or a user's first login) to their first realized benefit. | The onboarding metric that predicts adoption and advocacy. |
| Usability testing | Observing representative users attempting real tasks with a product to find where it fails them. | Five users will humble any confident design review. |
| User research | The disciplined study of users' needs, behaviors and contexts through interviews, observation and analysis. | The evidence base that earns product decisions credibility. |
| User story | A short requirement expressed from the user's perspective — "As a [role], I want [capability] so that [benefit]." | Keeps backlog items anchored to a person and a purpose. |
| Value proposition | A clear statement of the benefit a product delivers, to whom, and why it beats the alternatives. | If you cannot state it in a sentence, the product will drift. |
| Voice of the customer | The systematic collection and synthesis of client feedback from surveys, support, sales and research into decision-ready insight. | Turns scattered anecdotes into prioritization signal. |
| Win/loss analysis | Structured review of why deals were won or lost, drawing on client and sales input. | Digital experience is increasingly the deciding factor cited. |
| Wireframe | A low-fidelity structural sketch of a screen showing layout and hierarchy without visual polish. | The cheapest artifact for aligning on structure early. |
| WSJF (weighted shortest job first) | A prioritization method ranking work by cost of delay divided by job size, favoring high-value quick wins. | Useful where regulatory deadlines create real cost of delay. |

## 9. Technology and Architecture

| Term | Definition | Why it matters to you |
|---|---|---|
| ABAC (attribute-based access control) | Authorization that grants access based on evaluated attributes of the user, resource and context — e.g., role, client entitlement, data sensitivity, location. | The flexible model complex client entitlements eventually need. |
| API (application programming interface) | A defined contract through which software systems request data or actions from each other. | Your fastest-growing client channel alongside the portal. |
| API gateway | The managed entry point that routes, authenticates, throttles and monitors API traffic between consumers and backend services. | Where your API products get security and usage telemetry. |
| API-first | A design approach in which capabilities are built as APIs before (or alongside) any user interface consumes them. | Guarantees portal and client integrations share one truth. |
| Availability ("nines") | The percentage of time a service is operational — 99.9% ("three nines") allows about 8.8 hours of downtime per year, 99.99% about 53 minutes. | The reliability language of client SLAs you sign up to. |
| Batch processing | Executing work in scheduled bulk runs — the traditional overnight cycle of custody and fund accounting. | The legacy rhythm your real-time ambitions must coexist with. |
| Blue-green deployment | Releasing by running two identical environments and switching traffic from the old (blue) to the new (green), enabling instant rollback. | How your platforms ship changes without client-visible outages. |
| Canary release | Rolling out a change to a small slice of traffic first, watching health metrics before expanding to everyone. | Limits the blast radius of releases on client-facing systems. |
| CDC (change data capture) | Streaming row-level changes from a database's log to downstream consumers in near real time. | The pragmatic bridge from batch cores to real-time experiences. |
| Chaos engineering | Deliberately injecting failures into systems to verify they degrade and recover as designed. | Maturity signal for the resilience your clients depend on. |
| CI/CD (continuous integration / continuous delivery) | The automated pipeline that builds, tests and deploys every code change, keeping software releasable at all times. | Deployment frequency is a product velocity metric you track. |
| Circuit breaker | A resilience pattern that stops calling a failing dependency for a cooling-off period, preventing cascade failures. | Why one sick downstream feed should not take down your portal. |
| Cloud-native | Architecting applications specifically for cloud platforms — elastic, containerized, managed services, automated operations. | The design bar for everything new your teams build. |
| Container | A lightweight, portable package of an application and its dependencies that runs identically across environments. | The standard unit of deployment across your estate. |
| CQRS (command query responsibility segregation) | An architecture separating the write model (commands that change state) from the read model (queries), letting each be optimized independently. | How you serve fast, rich client views atop transactional cores. |
| DDoS (distributed denial of service) | An attack flooding a service with traffic from many sources to exhaust its capacity. | A standing threat to any internet-facing client platform. |
| DevSecOps | Integrating security controls and testing directly into the development and deployment pipeline rather than bolting them on at the end. | The only way to ship fast inside a G-SIB's control environment. |
| Disaster recovery (DR) | The capability to restore systems and data at an alternate site after a major failure, measured by recovery time objective (how quickly) and recovery point objective (how much data loss is tolerable). | Client due diligence will probe your products' DR posture. |
| Distributed tracing | Following a single request across every service it touches via propagated trace identifiers, to diagnose latency and errors. | How your teams answer "why was the portal slow at 9:03?" |
| Error budget | The acceptable amount of unreliability implied by a service-level objective — e.g., 99.9% allows 0.1% failure — spent deliberately on change and innovation. | The governance tool balancing release velocity against stability. |
| Event-driven architecture | Designing systems around the production and consumption of events — facts that something happened — enabling loose coupling and real-time reaction. | The architectural foundation of real-time client experiences. |
| Event sourcing | Persisting state as the append-only sequence of events that produced it, so current state can be rebuilt and history is complete by construction. | Native audit trail — a natural fit for regulated workflows. |
| Feature flag | A runtime switch that turns functionality on or off for specific users or segments without redeploying code. | Enables pilots, gradual rollouts and instant kill switches. |
| GraphQL | An API query language letting clients request exactly the fields they need in one call, served from a typed schema. | Attractive for data-dense dashboards; adds governance work. |
| Idempotency | The property that performing an operation multiple times has the same effect as performing it once, usually enforced with unique request keys. | Non-negotiable for payment and instruction APIs under retries. |
| IaC (infrastructure as code) | Defining infrastructure — networks, servers, permissions — in version-controlled code applied automatically, instead of manual configuration. | Auditability and repeatability your control functions require. |
| Kafka | The dominant open-source distributed event-streaming platform, storing ordered, replayable logs of events at scale. | Likely the backbone of your event and data streaming estate. |
| Kubernetes | The open-source orchestrator that schedules, scales and heals containerized applications across clusters. | The runtime platform decision beneath your product estate. |
| Latency | The time delay between a request and its response, typically tracked at percentiles such as p50 and p99. | Perceived product quality is largely tail latency. |
| Load balancer | A component distributing incoming traffic across multiple service instances for capacity and resilience. | Basic anatomy of how your platforms scale and survive failures. |
| Mainframe | Large, highly reliable centralized computers running decades-old core processing systems, often in COBOL. | Much custody truth still lives here; integration is your reality. |
| Message queue | Middleware that holds messages between producers and consumers, decoupling their availability and processing speed. | The asynchrony that keeps spikes from breaking workflows. |
| Microservices | An architecture decomposing an application into small, independently deployable services, each owning its data and lifecycle. | Enables team autonomy at the cost of operational complexity. |
| Micro-frontend | Applying microservice thinking to user interfaces: independently built and deployed page fragments composed into one experience. | How multiple teams ship into one portal without collisions. |
| Monolith | An application built and deployed as a single unit; simple to start, harder to scale organizationally. | Not a slur — sometimes the right answer; know the trade-offs. |
| mTLS (mutual TLS) | Transport-layer security in which both client and server authenticate each other with certificates before communicating. | Standard for service-to-service and B2B API security. |
| Multi-tenancy | Serving many customers from shared infrastructure while strictly isolating each tenant's data and configuration. | The economics of SaaS with the isolation bar of banking. |
| OAuth 2.0 | The standard framework by which a user or system grants an application scoped, revocable access to resources without sharing passwords. | The authorization plumbing of your API and portal ecosystem. |
| Observability | The ability to understand a system's internal state from its outputs — metrics, logs and traces — well enough to debug novel problems. | Prerequisite for the reliability your SLAs promise. |
| OIDC (OpenID Connect) | An identity layer on top of OAuth 2.0 that standardizes how applications verify who a user is via identity tokens. | How your portal knows, verifiably, who just logged in. |
| Orchestration vs choreography | Two coordination styles: a central controller directing each step (orchestration) versus services reacting independently to each other's events (choreography). | A recurring design debate in your workflow platforms. |
| Rate limiting | Restricting how many requests a consumer may make per time window, protecting services and enforcing fair use. | An API product policy decision, not just an infrastructure knob. |
| RBAC (role-based access control) | Authorization that grants permissions through assigned roles rather than to individuals directly. | The baseline entitlement model of every institutional portal. |
| REST | The dominant architectural style for web APIs, using standard HTTP verbs against resource URLs with stateless requests. | The default dialect of your public API surface. |
| Saga pattern | Managing a business transaction that spans multiple services as a sequence of local steps with compensating actions to undo partial work on failure. | How multi-step instructions stay consistent without 2-phase locks. |
| Sandbox | An isolated environment where clients or developers can safely test integrations against realistic but non-production data. | A first-class part of your API product's developer experience. |
| Scalability | A system's ability to handle growing load, either by adding instances (horizontal) or bigger machines (vertical). | Peak days — quarter-end, index rebalance — set your bar. |
| Schema registry | A central service storing versioned message schemas and enforcing compatibility rules as producers and consumers evolve. | The contract governance that keeps event streams from breaking. |
| SCIM (System for Cross-domain Identity Management) | The standard protocol for automating user provisioning and deprovisioning between identity systems and applications. | How client admins manage their users in your portal at scale. |
| SDLC (software development lifecycle) | The governed end-to-end process of specifying, building, testing, releasing and maintaining software. | The controlled path every feature must legitimately travel. |
| Secrets management | The secure storage, rotation and audited access of credentials, keys and tokens used by systems. | A hygiene item auditors and attackers both check first. |
| Service mesh | An infrastructure layer that transparently handles service-to-service traffic — mutual authentication, routing, retries, telemetry. | Uniform security and observability without per-team effort. |
| SLA (service level agreement) | A contractual commitment to service performance — availability, response times — with defined remedies for breach. | The promises your platform's engineering must underwrite. |
| SLI (service level indicator) | The actual measured value of a service behavior, such as the fraction of successful requests. | The raw measurement beneath objectives and agreements. |
| SLO (service level objective) | The internal target for a service level indicator — e.g., 99.9% of requests succeed — that engineering manages to. | The reliability contract between your product and platform teams. |
| SSO (single sign-on) | Authenticating once to access multiple applications, typically federated via standards such as SAML or OpenID Connect. | Enterprise clients require it before rollout, full stop. |
| Strangler fig | A modernization pattern that incrementally routes functionality from a legacy system to new services until the old system can be retired. | The realistic way to modernize custody platforms in flight. |
| Technical debt | The accumulated future cost of past expedient design and code choices, paid as slower and riskier change. | A portfolio liability you must budget to pay down explicitly. |
| Throughput | The volume of work a system processes per unit time — messages, transactions or requests per second. | Sizing language for peak processing conversations. |
| TLS (Transport Layer Security) | The cryptographic protocol securing data in transit between systems, successor to SSL. | Baseline encryption every connection you offer must use. |
| Versioning (API) | Managing change to API contracts so existing consumers keep working while new capabilities are introduced. | Breaking a client's integration is a relationship event. |
| WAF (web application firewall) | A filter inspecting web traffic for attack patterns — injection, cross-site scripting — before it reaches applications. | A standing control in front of your client-facing surfaces. |
| Webhook | An HTTP callback by which a system pushes event notifications to a subscriber's URL as things happen. | The simplest way clients get real-time events from you. |
| Zero trust | A security model that trusts no network location by default, verifying every user, device and request continuously. | The architecture direction of the whole firm's security estate. |

## 10. Data, Analytics and AI

| Term | Definition | Why it matters to you |
|---|---|---|
| Agent (AI) | An AI system that plans and executes multi-step tasks using tools, rather than answering a single prompt. | The next wave of copilot capability you'll be asked to evaluate. |
| Anomaly detection | Machine-learning techniques that flag data points deviating from learned normal patterns, such as an implausible NAV movement. | Augments tolerance checks in NAV and reconciliation oversight. |
| Bronze/silver/gold layers | A lakehouse convention staging data from raw (bronze) through cleaned (silver) to consumption-ready (gold). | Vocabulary for asking where in the pipeline a dataset sits. |
| Certified data source | A dataset formally designated as governed, quality-checked and owned — the official source for its domain. | Nothing client-facing should render from an uncertified source. |
| Data catalog | A searchable inventory of an organization's datasets, reports and their owners, definitions and certification status. | Answers "does governed client cash data already exist?" in minutes. |
| Data lake | A repository storing raw data in open formats at low cost, schema applied on read. | Cheap storage for everything; governance decides if it's usable. |
| Data lineage | The documented flow of data from origin through transformations to consumption. | Your fastest credible answer when a client challenges a number. |
| Data mart | A subject-specific, consumption-shaped slice of the warehouse, such as a client-reporting mart. | The layer your portal dashboards and feeds should read from. |
| Data mesh | An operating model treating data as products owned by domain teams rather than one central team. | The organizational debate behind many data-platform roadmaps. |
| Data product | A dataset managed like a product — owner, SLA, documentation, consumers, roadmap. | How client-facing data feeds and shares should be run. |
| Data quality dimensions | The standard lenses for assessing data: accuracy, completeness, timeliness, consistency, uniqueness, validity. | The shared vocabulary of every DQ scorecard you'll read. |
| Data residency | Legal requirements constraining where data may be stored or processed geographically. | Shapes architecture for any global portal or AI feature. |
| dbt | A widely used tool that manages SQL transformations in the warehouse with software-engineering discipline — version control, testing, documentation. | The de facto standard of the modern ELT stack. |
| Dimensional model | A warehouse design organizing data into fact tables (events, measures) and dimension tables (context) for fast analytics. | The shape behind almost every dashboard you'll govern. |
| Drift (model) | Degradation of a machine-learning model's accuracy as real-world data departs from its training data. | Why deployed models need monitoring, not just validation. |
| ELT | Extract-load-transform: land raw data in the warehouse first, transform there using its compute. | The modern default, replacing transform-first ETL. |
| Embedding | A numeric vector representing text or data such that similar meanings sit near each other, enabling semantic search. | The retrieval machinery under RAG and copilots. |
| Fact table | The center of a star schema: one row per business event (a settlement, a trade) with numeric measures and dimension keys. | "What's the grain of the fact?" is the analyst's first question. |
| Fine-tuning | Further training a foundation model on domain examples to specialize its behavior. | Rarely the first answer; RAG plus prompting usually wins in banks. |
| Foundation model | A large model pre-trained on broad data and adapted to many tasks, such as a large language model. | The platform layer of the AI stack; you buy, rarely build. |
| Grounding | Constraining an AI model's answer to supplied trusted context, with citations, rather than open-ended generation. | The difference between a deployable copilot and a liability. |
| Hallucination | A generative model producing fluent but false content. | The core client-facing AI risk; mitigated by grounding and review. |
| Human-in-the-loop | A workflow design where a person reviews or approves AI output before it takes effect. | The default pattern for anything client-impacting in a bank. |
| Lakehouse | An architecture combining lake storage economics with warehouse-style management and performance. | The convergence point of most modern platform roadmaps. |
| LLM (large language model) | A foundation model trained on text that generates and understands language — the engine of copilots and chat interfaces. | Product raw material; your job is the guardrails and the use case. |
| Master data management (MDM) | The discipline of maintaining one canonical record for core entities such as clients, securities and accounts. | Bad master data is the root cause of half of ops breaks. |
| Metrics/semantic layer | A single store of metric definitions (formula, grain, filters, owner) consumed by all BI tools and channels. | Prevents "two numbers disagree" — the worst analytics incident. |
| Model risk management | The governance of models — inventory, validation, monitoring — formalized in guidance like the Fed's SR 11-7. | Every AI feature you ship enters this regime; plan the timeline. |
| Prompt engineering | Designing the instructions and context given to a language model to shape reliable output. | Cheap first lever before fine-tuning; part of your teams' craft now. |
| RAG (retrieval-augmented generation) | Retrieving relevant, entitled documents or data first and having the model answer only from them, with citations. | The standard pattern for grounded, auditable copilots. |
| Row-level security | Filtering query results per viewer so each sees only their permitted rows from shared datasets and dashboards. | Must derive from the same entitlement model as the portal. |
| SR 11-7 | The Federal Reserve's supervisory guidance on model risk management: validation, documentation, ongoing monitoring. | The reason AI deployment in a bank takes longer than a startup. |
| Star schema | A dimensional model with a central fact table joined to surrounding dimension tables. | Read one ERD and you can navigate any analytics mart. |
| Time travel (Snowflake) | Querying data as it existed at a past point in time, within a retention window. | Instant answers to "what did the portal show last Tuesday?" |
| Token (AI) | The unit of text a language model processes and is priced by. | The cost driver of every AI feature's unit economics. |
| Vector database | A store optimized for similarity search over embeddings. | Infrastructure behind semantic search and RAG retrieval. |
| Virtual warehouse (Snowflake) | An independently sized and billed compute cluster querying shared storage. | The unit of Snowflake cost governance and workload isolation. |
| Zero-copy cloning | Creating instant, storage-free copies of databases for testing or experimentation. | Realistic test environments without doubling storage cost. |

## 11. Leadership, Finance and Corporate Vocabulary

| Term | Definition | Why it matters to you |
|---|---|---|
| Accretive | Adding to earnings or value; the opposite of dilutive. | Exec shorthand for "this deal/investment improves the numbers." |
| BAU (business as usual) | Ongoing run-the-bank activity, as distinct from change initiatives. | Funding conversations split every dollar into BAU vs change. |
| Basis point (bp) | One hundredth of one percent (0.01%). | The unit of custody fees, fund expenses and rate moves. |
| BLUF | Bottom line up front — stating the conclusion before the supporting detail. | The house style of effective executive communication. |
| Book of work | The portfolio of initiatives a team or division has committed to deliver. | What execs mean when they ask "what's on your book?" |
| Calibration | The comparative process by which committees align performance ratings and promotions across teams. | Where your promotion case is actually decided. |
| Capex vs opex | Capitalized investment spending versus operating expense; software work is often split between them. | Shapes how your funding is accounted for and defended. |
| Chargeback | Allocating central platform or technology costs to the business units consuming them. | Expect debates about your platform's cost allocation. |
| COO (chief operating officer) | The executive who owns operations; in clients, often your product's real buyer and escalation point. | Client COOs judge you on ops touches and incidents. |
| Cost-to-serve | The fully loaded cost of servicing a given client or activity. | The commercial metric your self-service products most directly move. |
| Cost of delay | The value lost per unit time by not shipping something — the numerator of WSJF. | Turns prioritization debates into economics. |
| Delta | The difference between two states or numbers. | "What's the delta?" = what changed / what's the gap. |
| Dilutive | Reducing per-share value or earnings, as unexercised rights issues do to holdings. | The word for what a missed corporate action costs. |
| EBIT / pre-tax margin | Earnings measures used to discuss profitability of a business line or deal. | The bottom line of the deal P&Ls your products influence. |
| EVP / SVP / MD | Executive vice president, senior vice president, managing director — senior officer tiers at banks (exact ladders vary). | The altitude map of your stakeholders and your career. |
| FTE (full-time equivalent) | A unit of workforce capacity equal to one full-time person. | Headcount — the currency of ops-efficiency business cases. |
| G-SIB | Global systemically important bank, designated by regulators and subject to heightened requirements. | Why your employer's control environment is stricter than a fintech's. |
| Guardrails | Pre-agreed boundaries within which a team may act autonomously. | How you delegate outcomes without micromanaging. |
| Hurdle rate | The minimum return an investment must clear to be approved. | Your business cases compete against it. |
| KPI / KRI | Key performance indicator (how well things run) / key risk indicator (early warning of risk). | Your dashboards will carry both; know which is which. |
| Line of business (LOB) | A distinct business unit with its own P&L, clients and leadership. | The organizing unit of strategy, funding and politics. |
| North star metric | The single metric that best captures the value a product delivers, from which supporting metrics cascade. | The top of your metrics tree; choose it carefully. |
| NPV (net present value) | The value today of a stream of future costs and benefits, discounted. | The math inside credible multi-year business cases. |
| Operating model | How an organization arranges people, processes, governance and technology to deliver. | Half your first-year battles are operating-model battles. |
| P&L (profit and loss) | The income statement of a business unit; also shorthand for owning revenue and cost accountability. | "Who owns the P&L?" determines who really decides. |
| Pre-wire | Briefing key stakeholders individually before a decision meeting so the forum confirms rather than discovers. | The single most useful meeting habit at VP level. |
| RACI / DACI | Frameworks assigning decision roles: responsible, accountable, consulted, informed (or driver, approver, contributors, informed). | Ends "I thought you had it" on cross-functional work. |
| Run rate | The annualized level of a cost or revenue based on its current pace. | How ongoing platform costs and savings are quoted. |
| Runway | How long current funding or capacity lasts at the present burn rate. | Applies to your change budget as much as to startups. |
| Sponsor | A senior leader who spends their own political capital advocating for a person or initiative. | Promotions and big initiatives move on sponsorship, not merit alone. |
| Steering committee | A senior forum that directs and unblocks a program or portfolio. | Run yours with named decisions and a decision log. |
| Synergies | Cost or revenue benefits from combining activities, often promised in reorganizations. | Treat claimed synergies with professional skepticism. |
| TCO (total cost of ownership) | The full lifetime cost of a system — build, run, support, exit. | The honest basis for build-vs-buy comparisons. |
| TOM (target operating model) | The designed future state of an organization's operating model. | The artifact big transformation programs are sold on. |
| Toll gate / stage gate | A formal checkpoint where a program must demonstrate readiness to proceed. | Your launches will pass through several; prepare evidence early. |
| Value driver tree | A decomposition of a business outcome into the measurable drivers that produce it. | Connects your roadmap to money in one diagram. |
| WSJF (weighted shortest job first) | A prioritization method ranking work by cost of delay divided by job size. | The scoring debate you'll referee every quarter. |

---

*End of glossary. Terms are defined for practical executive use; consult primary sources (regulations, standards, vendor documentation) where precision is legally material.*
