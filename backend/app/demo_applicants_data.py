"""Extra demo applicants + resume bodies for HR seeding (text resumes for reliable AI extraction)."""

# (username, password, job_offset 0=first job by id, resume_text, display_filename)
# Newest applicants are listed first in HR "top 5" when seeded with decreasing created_at.

DEMO_APPLICANTS: list[tuple[str, str, int, str, str]] = [
    (
        "taylor",
        "taylor",
        0,
        """TAYLOR NGUYEN
Staff Software Engineer

SUMMARY
10+ years building distributed systems and leading small teams. Recent focus on reliability, observability, and developer productivity.

EXPERIENCE
• Lead Engineer, Northwind Labs (2019–present): Owned payments pipeline (Python, Kafka, Postgres); cut incident MTTR 40%.
• Senior SWE, Blue Harbor (2014–2019): Java/Spring services; mentored 6 engineers.

SKILLS
Python, Go, SQL, AWS, Kubernetes, system design, technical writing.

EDUCATION
M.S. Computer Science""",
        "Taylor_Nguyen_Resume.txt",
    ),
    (
        "sam",
        "sam",
        0,
        """SAM OKONKWO
Machine Learning Engineer

PROFILE
ML engineer with 4 years shipping ranking and NLP features in production. Strong Python, PyTorch, and data pipelines.

EXPERIENCE
• ML Engineer, DataPulse (2021–present): Retrieval-augmented search; latency p99 −35%.
• Data Scientist, RetailCo (2019–2021): Forecasting models in scikit-learn and Spark.

SKILLS
Python, PyTorch, SQL, Airflow, AWS, A/B testing.

EDUCATION
B.S. Statistics""",
        "Sam_Okonkwo_Resume.txt",
    ),
    (
        "riley",
        "riley",
        0,
        """RILEY CHEN
Full-Stack Developer

SUMMARY
5 years TypeScript/React and Node APIs; comfortable owning features end-to-end.

EXPERIENCE
• Software Developer, BrightApps (2020–present): SaaS dashboard, GraphQL, Postgres.
• Junior Developer, StartSmall (2018–2020): REST APIs, Vue.js.

SKILLS
TypeScript, React, Node.js, PostgreSQL, Docker, CI/CD.

EDUCATION
B.A. Computer Science""",
        "Riley_Chen_Resume.txt",
    ),
    (
        "jordan",
        "jordan",
        0,
        """JORDAN PATEL
Frontend Engineer

ABOUT
Frontend specialist (6 years) focused on accessibility, design systems, and performance.

EXPERIENCE
• Senior FE, UIForge (2019–present): Component library used by 12 product teams.
• FE Developer, ClickStream (2017–2019): React + Redux marketing sites.

SKILLS
React, TypeScript, CSS, Web Vitals, Storybook, testing-library.

EDUCATION
B.S. Information Systems""",
        "Jordan_Patel_Resume.txt",
    ),
    (
        "morgan",
        "morgan",
        0,
        """MORGAN LEE
Software Developer (Career Switch)

PROFILE
Bootcamp graduate with 2 years internship + contract work. Eager, fast learner, strong communication.

EXPERIENCE
• Contract Developer, LocalShop (2023–present): Flask + SQLite inventory tool.
• Teaching Assistant, CodeCamp (2022): Supported 40 students in Python fundamentals.

PROJECTS
Open-source CLI tool for CSV cleanup (Python, 400+ GitHub stars).

SKILLS
Python, JavaScript, HTML/CSS, Git, basic AWS.

EDUCATION
Certificate, Full-Stack Web Development""",
        "Morgan_Lee_Resume.txt",
    ),
    (
        "alex",
        "alex",
        0,
        """ALEX RIVERA
Backend Engineer

SUMMARY
7 years Python and Go microservices; security-minded API design.

EXPERIENCE
• Backend Engineer, SecurePay (2018–present): PCI-scoped services, OAuth2, gRPC.
• Software Engineer, LogiSoft (2016–2018): Python Django monolith decomposition.

SKILLS
Python, Go, PostgreSQL, Redis, Docker, Linux.

EDUCATION
B.S. Software Engineering""",
        "Alex_Rivera_Resume.txt",
    ),
    (
        "casey",
        "casey",
        0,
        """CASEY WASHINGTON
Software Engineering Intern

EDUCATION
Junior, Computer Science — State University (expected 2026).

EXPERIENCE
• Summer Intern, TechTown (2025): Fixed 20+ bugs in internal React admin; wrote unit tests.
• Teaching Assistant: Data Structures (Python).

PROJECTS
Campus event app (React Native, Firebase).

SKILLS
Python, Java, JavaScript, React, Git.

INTERESTS
Open source, hackathons.""",
        "Casey_Washington_Resume.txt",
    ),
    (
        "priya",
        "priya",
        1,
        """PRIYA SHARMA
Associate Product Manager

SUMMARY
3 years PM/APM in B2B SaaS; shipped onboarding and billing improvements with measurable revenue impact.

EXPERIENCE
• APM, CloudLedger (2023–present): Defined specs for usage-based billing; aligned eng + design.
• Business Analyst, FinRight (2021–2023): SQL reporting, stakeholder workshops.

SKILLS
Roadmapping, SQL, Figma basics, agile, stakeholder management.

EDUCATION
MBA, Product concentration""",
        "Priya_Sharma_Resume.txt",
    ),
    (
        "dev",
        "dev",
        1,
        """DEV PATEL
Product Manager

PROFILE
5 years PM across mobile consumer and internal tools. Data-informed prioritization.

EXPERIENCE
• PM, PocketGames (2020–present): Live ops features; DAU +12% on core loop refresh.
• Associate PM, WorkGrid (2018–2020): Internal workflow automation.

SKILLS
SQL, Amplitude, Jira, prototyping, writing PRDs.

EDUCATION
B.S. Economics""",
        "Dev_Patel_Resume.txt",
    ),
]
