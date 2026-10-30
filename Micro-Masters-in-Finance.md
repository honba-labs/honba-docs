
Semester 1: Foundations & Analytical Toolkits

Duration: 12 Weeks | Target Focus: Advanced mathematical foundations, automated data pipelines, forensic accounting, market architecture, and asset pricing fundamentals.

🧭 Weekly Lecture Breakdown (Modules 1.1 – 1.6)


# Part 1.1: Mathematics for Finance

• Week 1: Foundations of Real Analysis
	• Lecture: Sets, functions, metric spaces, limits, sequences, and convergence of series in financial models.
	• Lab: Building automated sequence convergence visualizers for bond pricing limits.
• Week 2: Advanced Differential Calculus
	• Lecture: Partial differentiation, gradient vectors, Hessian matrices, and first/second-order Taylor expansions for multi-variable approximations.
	• Lab: Implementing Taylor series approximations for bond duration and convexity profiles.
• Week 3: Integral Calculus & Continuous Spaces
	• Lecture: Definite and indefinite integrals; Riemann sums; fundamental theorem of calculus; improper integrals in lifetime utility models.
	• Lab: Numerical integration of continuous probability densities using trapz/quad methods.
• Week 4: Linear Algebra Frameworks
	• Lecture: Vector spaces, matrix algebra, rank, determinants, and solving large-scale linear systems (Ax = b).
	• Lab: Coding Gaussian elimination and LU decomposition algorithms for asset allocation equations.
• Week 5: Spectral Theory & Matrix Decompositions
	• Lecture: Eigenvalues, eigenvectors, characteristic equations, and positive definiteness of covariance matrices.
	• Lab: Implementing singular value decomposition (SVD) to clean noisy financial correlation matrices.
• Week 6: Foundations of Unconstrained Optimization
	• Lecture: First-order and second-order optimality conditions; gradient descent; Newton-Raphson optimization algorithms.
	• Lab: Building a custom multi-variable gradient descent optimizer from scratch in pure Python.
• Week 7: Constrained Optimization & Duality
	• Lecture: Lagrange multipliers, economic interpretation of shadow prices, and equality-constrained optimization.
	• Lab: Solving optimal utility consumption problems under linear budget constraints.
• Week 8: Non-Linear Programming & Boundary Conditions
	• Lecture: Inequality constraints, Karush-Kuhn-Tucker (KKT) conditions, and complementary slackness theorems.
	• Lab: Coding a portfolio optimizer subject to mandatory minimum asset weight allocations.
• Week 9: Linear & Quadratic Programming
	• Lecture: Simplex algorithm mechanics, interior point methods, and quadratic objective functions with linear constraints.
	• Lab: Formulating and solving transaction-cost minimized asset rebalancing models using cvxpy.
• Week 10: Interpolation & Curve Fitting
	• Lecture: Polynomial interpolation, Lagrange forms, cubic splines, and numerical optimization errors.
	• Lab: Bootstrapping a smooth zero-coupon yield curve from discrete market bond yields using cubic splines.
• Week 11: Numerical Stability & Error Propagation
	• Lecture: Floating-point arithmetic, ill-conditioned matrices, condition numbers, and truncation vs. round-off errors.
	• Lab: Analyzing convergence decay in matrix inversion routines under high collinearity.
• Week 12: Comprehensive Math Review & Structural Assessment
	• Lecture: Synthesis of optimization and matrix decompositions in multi-asset class allocation frameworks.
	• Lab: Capstone Math Lab: Constructing a structural risk-factor optimization engine combining KKT and SVD.

# Part 1.2: Probability and Statistics

• Week 1: Axiomatic Probability & Conditioning
	• Lecture: Probability spaces (\(\Omega, \mathcal{F}, P\)), conditional probability, independence, and structural Bayes' theorem updates.
	• Lab: Coding a Bayesian inference script to update regime-shift probabilities based on market indicators.
• Week 2: Random Variables & Density Mechanics
	• Lecture: Discrete vs. continuous random variables, cumulative distribution functions (CDFs), and probability density functions (PDFs).
	• Lab: Mapping empirical asset return distributions against theoretical Gaussian distributions.
• Week 3: Parametric Distributions in Finance
	• Lecture: Binomial, Normal, Lognormal, and Student's t-distributions; heavy tails, skewness, and kurtosis profiles.
	• Lab: Fitting fat-tailed distributions to Nifty 50 crash data using Maximum Likelihood Estimation (MLE).
• Week 4: Expectations & Asymptotic Theorems
	• Lecture: Moments, covariance, joint distributions, Chebyshev's inequality, Law of Large Numbers (LLN), and Central Limit Theorem (CLT).
	• Lab: Simulating CLT convergence behavior by sampling non-normal asset return histories.
• Week 5: Sampling Distribution & Estimation Theory
	• Lecture: Unbiased estimators, efficiency, consistency, property of sufficiency, and mean squared error (MSE) minimizers.
	• Lab: Building standard error bootstrap simulators for historical asset volatility estimators.
• Week 6: Hypothesis Testing Frameworks
	• Lecture: Type I/II errors, p-values, t-tests, F-tests, Chi-square tests, and statistical power metrics.
	• Lab: Backtesting a basic momentum strategy anomaly using two-tailed t-tests for alpha significance.
• Week 7: Classical Linear Regression (OLS)
	• Lecture: Simple linear regression, Ordinary Least Squares (OLS) derivation, and the Gauss-Markov theorem.
	• Lab: Regressing individual stock returns against the Nifty index to calculate rolling historical market betas.
• Week 8: Multiple Linear Regression & Diagnostics
	• Lecture: Multi-variable OLS, R² vs. adjusted R², F-tests for joint significance, and matrix formulation of regression.
	• Lab: Building a multi-factor valuation model for equity pricing using macro inputs.
• Week 9: OLS Violation Analytics
	• Lecture: Detecting and fixing heteroskedasticity, multicollinearity (VIF), and autocorrelation (Durbin-Watson).
	• Lab: Implementing White’s heteroskedasticity-consistent standard errors in asset pricing models.
• Week 10: Stochastic Processes: Random Walks
	• Lecture: Introduction to discrete stochastic trends, white noise, random walks with drift, and efficient market representations.
	• Lab: Simulating 10,000 random walk price paths to assess long-term distribution variance drift.
• Week 11: Martingales & Conditional Expectations
	• Lecture: Martingale property, filtration concepts, stopping times, and fair-game assumptions in derivative pricing.
	• Lab: Testing option payoff expected values under risk-neutral probability distributions.
• Week 12: Econometric Model Validation
	• Lecture: Out-of-sample testing validation, structural break analysis (Chow test), and information criteria (AIC/BIC).
	• Lab: Evaluating model breakdown risk across historical market cycle inflection points.

# Part 1.3: Programming for Finance (Python)

• Week 1: Production Python Architecture
	• Lecture: Advanced object-oriented programming (OOP), memory management, environment isolation, and clean coding architectures.
	• Lab: Building an extensible vector-based financial asset class hierarchy with abstract base classes.
• Week 2: High-Performance Data Frameworks
	• Lecture: Vectorized computation patterns with NumPy; memory layouts, array slicing, and broadcasting mechanics.
	• Lab: Transforming raw tick logs into uniform arrays without iterative for-loops.
• Week 3: Advanced Data Wrangling with Pandas
	• Lecture: Time-series alignments, multi-indexing, resampling rules, merges, joins, and complex window functions.
	• Lab: Aligning unstructured, mismatched corporate action timelines across a 500-stock universe.
• Week 4: Automated Indian Market Data Ingestion
	• Lecture: API integrations, web scrapers, parsing complex JSON/XML schemas, and local storage configurations.
	• Lab: Building an automated script to download and parse NSE Bhavcopies and AMFI mutual fund data.
• Week 5: Corporate Action Data Normalization
	• Lecture: Adjusting historical pricing series for stock splits, bonus issues, dividends, and rights adjustments.
	• Lab: Programming an automated corporate action adjuster to output survivor-bias-free price series.
• Week 6: Exploratory Data Visualization & Engines
	• Lecture: Interactive dashboard compilation using Plotly, Matplotlib vector optimization, and Seaborn correlation plotting.
	• Lab: Building a dynamic interactive correlation heatmap dashboard for sectoral indices.
• Week 7: Numerical Algorithms & Roots Engines
	• Lecture: Implementing bisection, secant methods, and Newton-Raphson iterations in native vectorized Python.
	• Lab: Building a rapid implied volatility calculation engine using the Newton-Raphson method.
• Week 8: Performance Profiling & Optimization
	• Lecture: CPU/memory bottleneck profiling, space-time complexities, and compilation tricks using Numba.
	• Lab: Optimizing a slow Monte Carlo simulation engine by injecting numba.jit decorators.
• Week 9: Version Control & CI/CD Pipelines
	• Lecture: Git branching patterns, cherry-picking, markdown documentation, and automated testing architectures.
	• Lab: Writing unit tests with pytest for an open-source financial math library within Git workflows.
• Week 10: Production Logging & Exception Handling
	• Lecture: Structuring robust exception trees, fallback systems, automated alerts, and professional logging levels.
	• Lab: Deploying an ingestion script featuring persistent log rotation and database fault tolerance.
• Week 11: Relational Databases & SQL Engines
	• Lecture: Designing efficient database schemas, indexing strategies, SQL joins, and Python object-relational mapping (ORM).
	• Lab: Streaming historical price bars into a local SQLite/PostgreSQL database via SQLAlchemy.
• Week 12: Final Software Engineering System Delivery
	• Lecture: Packaging code libraries, dependency management via poetry, and microservice container deployment concepts.
	• Lab: Capstone Dev Lab: Deploying a fully packaged, tested, and containerized market data ingestion pipeline.

# Part 1.4: Financial Accounting and Corporate Reporting

• Week 1: Three-Statement Mechanics
	• Lecture: Deconstructing the Profit & Loss statement, Balance Sheet, and Cash Flow Statement relationships.
	• Lab: Building a dynamic, self-balancing three-statement model for a listed Indian firm.
• Week 2: Accrual Accounting & Revenue Recognition
	• Lecture: Matching principle, deferred revenue, long-term contracts, and aggressive income recognition mechanics.
	• Lab: Normalizing earnings for a real estate firm across volatile long-term contract timelines.
• Week 3: Working Capital & Asset Analysis
	• Lecture: Inventory valuation models, accounts receivable tracking, provisioning logic, and depreciation architectures.
	• Lab: Calculating cash conversion cycles (CCC) for competitive manufacturing companies.
• Week 4: Liability Structures & Off-Balance Sheet Debt
	• Lecture: Short vs. long-term debt, lease treatments, pension obligations, and contingent liabilities analysis.
	• Lab: Adjusting corporate leverage metrics to reflect off-balance sheet operating lease structures.
• Week 5: Advanced Ratio Analysis Matrices
	• Lecture: DuPont analysis decomposition, liquidity metrics, solvency ratios, and operating efficiency formulas.
	• Lab: Constructing an interactive programmatic dashboard tracking 5-year rolling DuPont metrics.
• Week 6: Structural Accounting Standards: Ind AS vs. IFRS
	• Lecture: Indian Accounting Standards (Ind AS) evolution, differences from Indian GAAP, and alignment with IFRS.
	• Lab: Translating an Indian firm's financial statement profile into pure IFRS compliance formats.
• Week 7: Forensic Accounting: Income Statement Disruption
	• Lecture: Identifying channel stuffing, capitalization of operating expenses, and non-operating income tricks.
	• Lab: Developing a programmatic algorithm calculating the Beneish M-Score across a sectoral index.
• Week 8: Forensic Accounting: Balance Sheet Manipulation
	• Lecture: Inventory build-ups, sudden asset revaluations, goodwill impairments, and bad debt provision manipulation.
	• Lab: Building an automated screener checking for sudden spikes in Days Sales Outstanding (DSO).
• Week 9: Corporate Governance Red Flags
	• Lecture: Related-party transactions (RPTs), promoter share pledging, unhedged foreign debt, and management turnover.
	• Lab: Scraping exchange disclosures to track real-time changes in promoter share pledging profiles.
• Week 10: Auditor Audit Diagnostics
	• Lecture: Evaluating qualified opinions, internal control weaknesses, sudden auditor resignations, and fee anomalies.
	• Lab: Building a NLP textual risk-tagger parsing auditor statements in annual reports.
• Week 11: Integrated Earnings Quality Assessments
	• Lecture: Divergence vectors between net accounting profit and actual operating cash flow dynamics.
	• Lab: Developing an automated index ranking firms based on their accrual-to-cash ratios.
• Week 12: Comprehensive Forensic Valuation Capstone
	• Lecture: Synthesizing forensic screening outcomes directly into standard financial valuation discounting assumptions.
	• Lab: Deconstructing an institutional corporate collapse case study (e.g., DHFL, IL&FS) using forensic tools.

# Part 1.5: Indian Financial Markets and Institutions

• Week 1: Market Topography & Infrastructure
	• Lecture: Primary vs. secondary markets; institutional clearing corporations (NSCCL), depositories (NSDL, CDSL), and exchange setups (NSE, BSE).
	• Lab: Mapping the structural transaction path of an order from trade matching to ultimate settlement.
• Week 2: Microstructure Execution & Frictions
	• Lecture: Order books, limit vs. market orders, matching engine rules, auction mechanics, and trade lifecycle steps.
	• Lab: Processing a raw order-book data stream to map real-time bid-ask spread variations.
• Week 3: Institutional Regulatory Ecosystem
	• Lecture: Legal remits and jurisdictions of SEBI, RBI, and IRDAI; statutory monitoring limits.
	• Lab: Simulating compliance validations for institutional portfolios under SEBI mutual fund group exposure limits.
• Week 4: Market Participant Architecture
	• Lecture: FPI/FII frameworks, DII (Mutual funds, LIC) configurations, proprietary trading desks, and retail pathways.
	• Lab: Building an institutional money flow tracker parsing daily exchange FII/DII data streams.
• Week 5: Post-Trade Clearing & Settlement Friction
	• Lecture: T+1 settlement mechanics, margining systems (VaR, Extreme Loss margins), and short-delivery auctions.
	• Lab: Coding an automated institutional transaction calculator computing net delivery obligations.
• Week 6: Complete Transaction Friction Breakdown
	• Lecture: Securities Transaction Tax (STT), exchange charges, SEBI turnover fees, GST, stamp duty, and slippage.
	• Lab: Building a production cost model calculating the exact breakeven distance for an algorithmic strategy.
• Week 7: Indian Financial Product Universe
	• Lecture: Equity shares, corporate bonds, mutual funds, ETFs, Funds of Funds (FoF), AIFs (Cat I/II/III), and PMS setups.
	• Lab: Compiling a tracking comparison engine analyzing expense drag vs. tracking error across Indian ETFs.
• Week 8: Structural Index Architectures
	• Lecture: Free-float market capitalization methodology, rebalancing rules, Nifty 50, Sensex, and the India VIX calculation framework.
	• Lab: Programming a clone engine replicating Nifty 50 index weight rebalancings from raw market caps.
• Week 9: Primary Markets & The IPO Lifecycle
	• Lecture: Book building mechanics, red herring prospectuses (DRHP), anchor allocations, listing gains, and regulations.
	• Lab: Evaluating listing day pricing variations against historical anchor investor subscription profiles.
• Week 10: SEBI LODR Compliance Framework
	• Lecture: Listing Obligations and Disclosure Requirements (LODR); price-sensitive disclosures, insider trading preventions (PIT).
	• Lab: Building a monitoring system tracking corporate disclosures using stock exchange RSS feeds.
• Week 11: Companies Act 2013 Governance Mandates
	• Lecture: Legal protections for minority shareholders, board compositions, audit committee structures, and capital reduction paths.
	• Lab: Parsing corporate resolutions to flag potential minority-promoter governance alignment conflicts.
• Week 12: Macro Institutional System Review
	• Lecture: Analyzing systemic risk propagation points across banking, shadow banking (NBFCs), and capital markets.
	• Lab: Institutional Lab: Simulating a multi-market systemic liquidity shock across clearing house configurations.

# Part 1.6: Finance Theory I

• Week 1: Foundations of Time Value of Money
	• Lecture: Compounding frequencies, continuous compounding, present value derivations, and annuities/perpetuities.
	• Lab: Building a custom amortization calculator engine for structured debt instruments.
• Week 2: Capital Budgeting & The NPV Decision Rule
	• Lecture: Net Present Value (NPV) foundations, Internal Rate of Return (IRR), payback periods, and capital allocations.
	• Lab: Developing an automated alternative investment ranker comparing conflicting NPV and IRR projects.
• Week 3: Advanced Fixed Income Pricing Fundamentals
	• Lecture: Bond pricing formulas, Yield to Maturity (YTM) mathematical roots, spot rates, and term structure shapes.
	• Lab: Coding a numerical solver engine to extract exact YTM values from coupon-paying bonds.
• Week 4: Equity Valuation: Dividend Discount Paradigms
	• Lecture: Dividend discount models, multi-stage Gordon growth models, and implied growth rate extractions.
	• Lab: Building an equity valuation model with dynamic terminal growth transitions.
• Week 5: Absolute Intro to Derivative Payoffs
	• Lecture: Forward commitments, futures settlement rules, and elementary boundary options conditions (put-call parity).
	• Lab: Visualizing multi-leg derivative expiration payoff grids programmatically.
• Week 6: Modern Portfolio Theory: Risk-Return Profiles
	• Lecture: Defining mathematical risk, diversification effects, asset correlation matrices, and joint variances.
	• Lab: Mapping the full risk-return investment universe across a randomized 10-asset weight layout.
• Week 7: Mean-Variance Optimization Models
	• Lecture: Analytical derivation of the efficient frontier, global minimum variance portfolios, and optimal portfolios.
	• Lab: Computing the analytical Sharpe-maximizing tangency portfolio under short-sale bans.
• Week 8: Capital Asset Pricing Model (CAPM)
	• Lecture: Core assumptions, risk-free borrowing, derivation of the Capital Market Line (CML) and Security Market Line (SML).
	• Lab: Programmatically estimating empirical alpha and beta metrics for a large-cap stock universe.
• Week 9: Capital Budgeting Cash Flow Engineering
	• Lecture: Estimating relevant incremental cash flows, terminal values, working capital changes, and inflation adjustments.
	• Lab: Modeling 10-year free cash flows for a new infrastructure manufacturing project.
• Week 10: Advanced Project Interaction Decisions
	• Lecture: Evaluating mutually exclusive investments with unequal lifespans, replacement cycles, and optimal abandonments.
	• Lab: Building an equivalent annual annuity (EAA) calculator for capital equipment budgeting.
• Week 11: Structural Risk Diagnostics in Capital Budgeting
	• Lecture: Sensitivity analysis, scenario planning, break-even analytics, and simulation frameworks.
	• Lab: Programming a 50,000-iteration Monte Carlo valuation simulation for a volatile mining project.
• Week 12: Unified Finance Theory Synthesizer
	• Lecture: Connecting corporate investment hurdle rates directly with public asset pricing models (CAPM/WACC).
	• Lab: Capstone Asset Theory Lab: Constructing a corporate valuation engine that dynamically adjusts discount rates based on rolling equity betas.

📚 Comprehensive Reference Blueprint

To ensure deep analytical rigor, the course material is mapped directly to the standard academic texts below.
+-----------------------------------+-----------------------------------+-----------------------------------+

|# Part                            | Core Academic Textbook            | Alternative / Professional Text   |
+-----------------------------------+-----------------------------------+-----------------------------------+

| 1.1 Mathematics for Finance       | "Mathematics for Economists"      | "Foundations of Mathematical      |
|                                   | - Simon & Blume                   | Economics" - Michael Carter       |
+-----------------------------------+-----------------------------------+-----------------------------------+

| 1.2 Probability and Statistics    | "Statistical Inference"           | "Introductory Econometrics"       |
|                                   | - Casella & Berger                | - Jeffrey Wooldridge              |
+-----------------------------------+-----------------------------------+-----------------------------------+

| 1.3 Programming for Finance       | "Python for Data Analysis"        | "Python for Finance"              |
|                                   | - Wes McKinney                    | - Yves Hilpisch                   |
+-----------------------------------+-----------------------------------+-----------------------------------+

| 1.4 Financial Accounting          | "Financial Reporting & Analysis"  | "Corporate Financial Reporting    |
|                                   | - Lawrence Revsine                | & Analysis" - David Young         |
+-----------------------------------+-----------------------------------+-----------------------------------+

| 1.5 Indian Financial Markets      | "Financial Markets & Inst."       | SEBI Manual, NISM Series Workbook |
|                                   | - Anthony Saunders                | (VIII / X / XII)                  |
+-----------------------------------+-----------------------------------+-----------------------------------+

| 1.6 Finance Theory I              | "Principles of Corporate Finance" | "Financial Theory & Corporate     |
|                                   | - Brealey, Myers, & Allen         | Policy" - Copeland & Weston       |
+-----------------------------------+-----------------------------------+-----------------------------------+
