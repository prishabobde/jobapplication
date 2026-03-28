"""Seed rows for the jobs table (title, description, department, location, employment_type)."""

JOB_SEEDS: list[tuple[str, str, str, str, str]] = [
    (
        "Software Dev",
        """Design, build, and maintain web services and internal tools that power Prisha Company's products. You will work across the stack—APIs, data models, and polished UI components—partnering with product and design in short iteration cycles.

We expect solid fundamentals in modern languages (e.g. Python, TypeScript, or similar), experience with relational databases, and comfort reviewing others' code with empathy. You care about reliability, observability, and clear documentation.

Day to day you will ship features, fix production issues when needed, and help improve our engineering standards. This is a collaborative role: communication and ownership matter as much as technical depth.""",
        "Engineering",
        "Hybrid — San Francisco Bay Area",
        "Full-time",
    ),
    (
        "Product Manager",
        """Own discovery and delivery for a product area from problem framing through launch. You will run research conversations, write crisp requirements, align stakeholders, and work with engineering to sequence work that balances user value and business outcomes.

You should have experience shipping software in cross-functional teams, using both qualitative feedback and metrics to decide what to build next. Comfort with ambiguity and strong written communication are essential.

You will partner closely with design, engineering, and go-to-market teams to define roadmaps, measure success, and iterate based on what you learn in market.""",
        "Product",
        "Remote (US)",
        "Full-time",
    ),
    (
        "ML Engineer",
        """Build and operate machine learning systems that move from notebook to production: training pipelines, evaluation, deployment, and monitoring. You will collaborate with product and data teams to identify high-impact modeling problems and ship robust solutions.

We look for experience with Python ML stacks, feature and model lifecycle practices, and sound judgment about when simple baselines beat complex models. Exposure to LLMs, retrieval, or recommendation systems is a plus.

You will help set technical direction for ML infrastructure, improve reproducibility, and ensure our models are fair, explainable where needed, and maintainable by the broader team.""",
        "Engineering / AI",
        "Hybrid — San Francisco Bay Area",
        "Full-time",
    ),
    (
        "HR",
        """Support the full employee lifecycle at Prisha Company: recruiting coordination, onboarding, policies, employee relations, and programs that keep our culture inclusive and high-trust. You will be a partner to managers and a resource for everyone on the team.

Ideal candidates bring experience in a fast-moving company, strong judgment on sensitive matters, and excellent organizational skills. Familiarity with ATS tools, compliance basics, and people analytics is helpful.

You will help scale our people practices as we grow, run engagement initiatives, and ensure our processes stay simple, fair, and well communicated.""",
        "People & Talent",
        "On-site — San Francisco",
        "Full-time",
    ),
    (
        "Financial Analyst",
        """Drive forecasting, budgeting, and reporting so leadership can make fast, informed decisions. You will own models for revenue and operating expenses, support board and investor materials, and partner with department heads on variance analysis.

We need strong Excel / spreadsheet modeling skills, attention to detail, and the ability to translate numbers into clear narratives. Experience with ERP or planning tools and a background in SaaS or high-growth environments is preferred.

You will improve financial processes, automate recurring reports where possible, and help build a culture of fiscal discipline without slowing the business down.""",
        "Finance",
        "Hybrid — San Francisco Bay Area",
        "Full-time",
    ),
]
