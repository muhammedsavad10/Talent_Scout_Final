import re
from typing import Dict, List, Any

ONTOLOGY_VERSION = "2.0"

EMAIL_PATTERN = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
PHONE_PATTERN = re.compile(r'\+?\d[\d\-\(\)\s]{8,14}\d')
URL_PATTERN = re.compile(r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*)')

SKILL_ONTOLOGY = {
    "programming_languages": {
        "python": "Python", "javascript": "JavaScript", "typescript": "TypeScript",
        "java": "Java", "c++": "C++", "c#": "C#", "go": "Go", "rust": "Rust",
        "ruby": "Ruby", "php": "PHP", "swift": "Swift", "kotlin": "Kotlin",
        "scala": "Scala", "perl": "Perl", "haskell": "Haskell", "lua": "Lua",
        "dart": "Dart", "elixir": "Elixir", "clojure": "Clojure", "groovy": "Groovy",
        "r": "R", "matlab": "MATLAB", "sql": "SQL", "assembly": "Assembly",
        "shell": "Shell", "bash": "Bash", "powershell": "PowerShell", "solidity": "Solidity",
        "delphi": "Delphi", "objective c": "Objective-C", "cuda": "CUDA",
        "julia": "Julia", "fortran": "Fortran", "cobol": "COBOL", "pl/sql": "PL/SQL",
        "sas": "SAS", "spss": "SPSS", "vb.net": "VB.NET", "f#": "F#",
        "apex": "Apex", "abap": "ABAP"
    },
    "frontend_frameworks": {
        "react": "React", "reactjs": "React", "react.js": "React",
        "angular": "Angular", "angularjs": "AngularJS", "vue": "Vue.js", "vuejs": "Vue.js",
        "svelte": "Svelte", "nextjs": "Next.js", "next.js": "Next.js",
        "nuxtjs": "Nuxt.js", "gatsby": "Gatsby", "ember": "Ember",
        "backbone": "Backbone.js", "jquery": "jQuery", "htmx": "HTMX",
        "alpinejs": "Alpine.js", "solidjs": "Solid.js", "qwik": "Qwik",
        "redux": "Redux", "mobx": "MobX", "tailwind": "Tailwind CSS",
        "bootstrap": "Bootstrap", "material ui": "Material UI", "mui": "MUI",
        "chakra ui": "Chakra UI", "styled components": "Styled Components",
        "sass": "Sass", "scss": "SCSS", "less": "Less", "css": "CSS", "html": "HTML"
    },
    "backend_frameworks": {
        "fastapi": "FastAPI", "django": "Django", "flask": "Flask",
        "spring": "Spring", "spring boot": "Spring Boot", "express": "Express.js",
        "node.js": "Node.js", "nodejs": "Node.js", "deno": "Deno",
        "asp.net": "ASP.NET", "asp.net core": "ASP.NET Core", ".net": ".NET",
        ".net core": ".NET Core", "laravel": "Laravel", "rails": "Ruby on Rails",
        "ruby on rails": "Ruby on Rails", "gin": "Gin", "echo": "Echo",
        "fiber": "Fiber", "actix": "Actix", "rocket": "Rocket",
        "ktor": "Ktor", "play": "Play Framework", "dropwizard": "Dropwizard",
        "graphql": "GraphQL", "apollo": "Apollo", "rest": "REST API",
        "grpc": "gRPC", "tornado": "Tornado", "aiohttp": "aiohttp",
        "sanic": "Sanic", "quart": "Quart", "celery": "Celery"
    },
    "cloud_platforms": {
        "aws": "AWS", "amazon web services": "AWS", "gcp": "GCP",
        "google cloud": "Google Cloud", "azure": "Azure", "microsoft azure": "Azure",
        "heroku": "Heroku", "digitalocean": "DigitalOcean", "linode": "Linode",
        "vultr": "Vultr", "cloudflare": "Cloudflare", "vercel": "Vercel",
        "netlify": "Netlify", "render": "Render", "fly.io": "Fly.io",
        "oracle cloud": "Oracle Cloud", "ibm cloud": "IBM Cloud",
        "alibaba cloud": "Alibaba Cloud", "supabase": "Supabase",
        "firebase": "Firebase", "aws lambda": "AWS Lambda", "lambda": "AWS Lambda",
        "ec2": "AWS EC2", "s3": "AWS S3", "ecs": "AWS ECS", "eks": "AWS EKS",
        "fargate": "AWS Fargate", "cloudfront": "CloudFront",
        "cloudformation": "CloudFormation", "terraform": "Terraform"
    },
    "databases": {
        "postgresql": "PostgreSQL", "postgres": "PostgreSQL", "mysql": "MySQL",
        "mongodb": "MongoDB", "redis": "Redis", "elasticsearch": "Elasticsearch",
        "cassandra": "Cassandra", "dynamodb": "DynamoDB", "firestore": "Firestore",
        "cosmosdb": "Cosmos DB", "mariadb": "MariaDB", "sqlite": "SQLite",
        "oracle": "Oracle DB", "sql server": "SQL Server", "mssql": "SQL Server",
        "db2": "IBM DB2", "couchbase": "Couchbase", "neo4j": "Neo4j",
        "arangodb": "ArangoDB", "influxdb": "InfluxDB", "timescaledb": "TimescaleDB",
        "clickhouse": "ClickHouse", "snowflake": "Snowflake", "bigquery": "BigQuery",
        "redshift": "Redshift", "hive": "Hive", "hbase": "HBase",
        "presto": "Presto", "trino": "Trino", "qdrant": "Qdrant",
        "pinecone": "Pinecone", "weaviate": "Weaviate", "milvus": "Milvus",
        "chromadb": "ChromaDB", "faiss": "FAISS", "couchdb": "CouchDB"
    },
    "devops_tools": {
        "docker": "Docker", "kubernetes": "Kubernetes", "k8s": "Kubernetes",
        "jenkins": "Jenkins", "github actions": "GitHub Actions", "gitlab ci": "GitLab CI",
        "circleci": "CircleCI", "travis ci": "Travis CI", "argo": "ArgoCD",
        "helm": "Helm", "ansible": "Ansible", "chef": "Chef", "puppet": "Puppet",
        "saltstack": "SaltStack", "nginx": "Nginx", "apache": "Apache",
        "istio": "Istio", "linkerd": "Linkerd", "envoy": "Envoy",
        "consul": "Consul", "vault": "Vault", "prometheus": "Prometheus",
        "grafana": "Grafana", "datadog": "Datadog", "new relic": "New Relic",
        "elk": "ELK Stack", "elastic stack": "ELK Stack", "kibana": "Kibana",
        "logstash": "Logstash", "jaeger": "Jaeger", "opentelemetry": "OpenTelemetry",
        "git": "Git", "github": "GitHub", "gitlab": "GitLab", "bitbucket": "Bitbucket",
        "sonarqube": "SonarQube", "nexus": "Nexus", "jfrog": "JFrog Artifactory"
    },
    "ml_ai": {
        "machine learning": "Machine Learning", "deep learning": "Deep Learning",
        "natural language processing": "NLP", "nlp": "NLP",
        "computer vision": "Computer Vision", "pytorch": "PyTorch",
        "tensorflow": "TensorFlow", "keras": "Keras", "scikit-learn": "Scikit-Learn",
        "sklearn": "Scikit-Learn", "xgboost": "XGBoost", "lightgbm": "LightGBM",
        "catboost": "CatBoost", "langchain": "LangChain", "llamaindex": "LlamaIndex",
        "hugging face": "Hugging Face", "transformers": "Transformers",
        "spacy": "spaCy", "nltk": "NLTK", "opencv": "OpenCV", "yolo": "YOLO",
        "rag": "RAG", "retrieval augmented generation": "RAG",
        "llm": "LLM", "large language model": "LLM",
        "openai": "OpenAI", "ollama": "Ollama", "groq": "Groq",
        "stable diffusion": "Stable Diffusion", "generative ai": "Generative AI",
        "mlops": "MLOps", "feature engineering": "Feature Engineering",
        "hyperparameter tuning": "Hyperparameter Tuning", "model deployment": "Model Deployment",
        "model serving": "Model Serving", "onnx": "ONNX", "triton": "Triton Inference Server",
        "mlflow": "MLflow", "kubeflow": "Kubeflow", "airflow": "Airflow",
        "pandas": "pandas", "numpy": "NumPy", "scipy": "SciPy",
        "matplotlib": "Matplotlib", "seaborn": "Seaborn", "plotly": "Plotly",
        "dash": "Dash", "streamlit": "Streamlit", "gradio": "Gradio",
        "opencv": "OpenCV", "pillow": "Pillow", "librosa": "Librosa"
    },
    "data_engineering": {
        "apache spark": "Apache Spark", "spark": "Apache Spark",
        "hadoop": "Hadoop", "kafka": "Kafka", "apache kafka": "Kafka",
        "flink": "Apache Flink", "storm": "Apache Storm", "beam": "Apache Beam",
        "airflow": "Apache Airflow", "nifi": "Apache NiFi",
        "dbt": "dbt", "etl": "ETL", "data pipeline": "Data Pipeline",
        "data warehouse": "Data Warehouse", "data lake": "Data Lake",
        "data mesh": "Data Mesh", "delta lake": "Delta Lake",
        "databricks": "Databricks", "hive": "Apache Hive", "impala": "Impala",
        "tableau": "Tableau", "power bi": "Power BI", "looker": "Looker",
        "qlik": "Qlik", "metabase": "Metabase", "superset": "Superset"
    },
    "testing": {
        "jest": "Jest", "pytest": "pytest", "unittest": "unittest",
        "mocha": "Mocha", "chai": "Chai", "cypress": "Cypress",
        "playwright": "Playwright", "selenium": "Selenium", "puppeteer": "Puppeteer",
        "junit": "JUnit", "testng": "TestNG", "mockito": "Mockito",
        "jasmine": "Jasmine", "karma": "Karma", "vitest": "Vitest",
        "cucumber": "Cucumber", "gherkin": "Gherkin", "postman": "Postman",
        "soapui": "SoapUI", "locust": "Locust", "jmeter": "JMeter",
        "k6": "k6", "gatling": "Gatling", "sonarqube": "SonarQube"
    },
    "mobile": {
        "android": "Android", "ios": "iOS", "react native": "React Native",
        "flutter": "Flutter", "swiftui": "SwiftUI", "uikit": "UIKit",
        "xcode": "Xcode", "kotlin multiplatform": "Kotlin Multiplatform",
        "ionic": "Ionic", "cordova": "Cordova", "xamarin": "Xamarin",
        "unity": "Unity", "unreal": "Unreal Engine", "ar": "AR", "vr": "VR"
    },
    "security": {
        "cybersecurity": "Cybersecurity", "penetration testing": "Penetration Testing",
        "owasp": "OWASP", "siem": "SIEM", "soc": "SOC",
        "identity management": "Identity Management", "oauth": "OAuth",
        "jwt": "JWT", "saml": "SAML", "openid": "OpenID",
        "encryption": "Encryption", "ssl": "SSL", "tls": "TLS",
        "vpn": "VPN", "firewall": "Firewall", "intrusion detection": "Intrusion Detection"
    },
    "soft_skills": {
        "leadership": "Leadership", "team management": "Team Management",
        "project management": "Project Management", "agile": "Agile",
        "scrum": "Scrum", "kanban": "Kanban", "jira": "Jira",
        "confluence": "Confluence", "communication": "Communication",
        "mentoring": "Mentoring", "technical writing": "Technical Writing",
        "code review": "Code Review", "system design": "System Design",
        "architecture": "Architecture", "microservices": "Microservices",
        "restful": "RESTful", "api design": "API Design", "documentation": "Documentation",
        "problem solving": "Problem Solving", "critical thinking": "Critical Thinking"
    },
    "protocols_standards": {
        "http": "HTTP", "https": "HTTPS", "tcp/ip": "TCP/IP", "udp": "UDP",
        "websocket": "WebSocket", "mqtt": "MQTT", "amqp": "AMQP",
        "rest": "REST", "soap": "SOAP", "graphql": "GraphQL",
        "protobuf": "Protocol Buffers", "avro": "Avro", "parquet": "Parquet",
        "json": "JSON", "xml": "XML", "yaml": "YAML", "toml": "TOML",
        "csv": "CSV", "markdown": "Markdown", "html": "HTML", "css": "CSS"
    }
}

def extract_contact_info(text: str) -> Dict[str, Any]:
    emails = EMAIL_PATTERN.findall(text)
    phones = PHONE_PATTERN.findall(text)
    links = URL_PATTERN.findall(text)

    def dedupe(seq):
        seen = set()
        return [x for x in seq if not (x in seen or seen.add(x))]

    return {
        "email": emails[0] if emails else None,
        "phone": phones[0].strip() if phones else None,
        "links": dedupe(links)
    }

def extract_known_skills(text: str, known_ontology: List[str]) -> List[str]:
    extracted = []
    text_lower = text.lower()
    for skill in known_ontology:
        escaped_skill = re.escape(skill.lower())
        pattern = re.compile(rf'\b{escaped_skill}\b')
        if pattern.search(text_lower):
            extracted.append(skill)
    return extracted

def _text_contains_skill(text_lower: str, skill_key: str) -> bool:
    try:
        return bool(re.search(r'\b' + re.escape(skill_key) + r'\b', text_lower))
    except re.error:
        return skill_key in text_lower

def extract_skills_deterministically(text: str, source: str) -> List[Dict[str, Any]]:
    if not text:
        return []
    text_lower = text.lower()
    found = []
    seen_names = set()

    for category, skills in SKILL_ONTOLOGY.items():
        for skill_key, skill_name in skills.items():
            normalized_key = skill_key.lower()
            if normalized_key in seen_names:
                continue
            if _text_contains_skill(text_lower, normalized_key):
                seen_names.add(normalized_key)
                found.append({
                    "name": skill_name,
                    "category": category,
                    "confidence": 90,
                    "categories": [category]
                })

    return found

def extract_certifications_deterministically(text: str) -> List[Dict[str, str]]:
    if not text:
        return []
    certs = []
    patterns = [
        (r'(?:AWS\s+Certified\s+[\w\s-]+)', "AWS Certified"),
        (r'(?:Certified\s+Kubernetes\s+Administrator)', "CKA"),
        (r'(?:Certified\s+Kubernetes\s+Application\s+Developer)', "CKAD"),
        (r'(?:Google\s+Cloud\s+Certified\s+[\w\s-]+)', "Google Cloud Certified"),
        (r'(?:Microsoft\s+Certified\s+[\w\s-]+)', "Microsoft Certified"),
        (r'(?:Azure\s+[\w\s-]+\s+Certification)', "Azure Certified"),
        (r'(?:CISSP)', "CISSP"),
        (r'(?:CompTIA\s+[\w+]+)', "CompTIA"),
        (r'(?:PMP)', "PMP"),
        (r'(?:Certified\s+ScrumMaster)', "CSM"),
        (r'(?:SAFe\s+\w+)', "SAFe"),
        (r'(?:TOGAF)', "TOGAF"),
        (r'(?:ITIL)', "ITIL"),
        (r'(?:Oracle\s+Certified)', "Oracle Certified"),
        (r'(?:Red\s+Hat\s+Certified)', "Red Hat Certified"),
        (r'(?:Cisco\s+Certified)', "Cisco Certified"),
        (r'(?:CCNA)', "CCNA"),
        (r'(?:CCNP)', "CCNP"),
        (r'(?:AWS\s+Solutions\s+Architect)', "AWS Solutions Architect"),
        (r'(?:AWS\s+Developer\s+Associate)', "AWS Developer Associate"),
        (r'(?:AWS\s+DevOps\s+Engineer)', "AWS DevOps Engineer"),
        (r'(?:Professional\s+Cloud\s+Architect)', "Professional Cloud Architect"),
        (r'(?:Data\s+Engineer\s+Certification)', "Data Engineer Certification"),
        (r'(?:Machine\s+Learning\s+Certification)', "ML Certification"),
        (r'(?:TensorFlow\s+Certificate)', "TensorFlow Certificate"),
        (r'(?:Certified\s+Data\s+Analyst)', "Certified Data Analyst"),
        (r'(?:Tableau\s+Certified)', "Tableau Certified"),
        (r'(?:Salesforce\s+Certified)', "Salesforce Certified"),
        (r'(?:Kubernetess?\s+Certification)', "Kubernetes Certification"),
        (r'(?:HashiCorp\s+Certified)', "HashiCorp Certified"),
        (r'(?:Terraform\s+Associate)', "Terraform Associate"),
        (r'(?:ISTQB)', "ISTQB"),
        (r'(?:Certified\s+Ethical\s+Hacker)', "CEH"),
        (r'(?:CEH)', "CEH"),
        (r'(?:OSCP)', "OSCP"),
    ]
    for pattern, title in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            if not any(c["title"] == title for c in certs):
                certs.append({"title": title})
    return certs

def extract_languages_deterministically(text: str) -> List[str]:
    if not text:
        return []
    languages = []
    known_languages_list = [
        "English", "Spanish", "French", "German", "Mandarin", "Chinese",
        "Japanese", "Korean", "Hindi", "Arabic", "Portuguese", "Russian",
        "Italian", "Dutch", "Polish", "Turkish", "Vietnamese", "Thai",
        "Swedish", "Norwegian", "Danish", "Finnish", "Greek", "Hebrew",
        "Bengali", "Urdu", "Punjabi", "Tamil", "Telugu", "Malayalam",
        "Marathi", "Gujarati", "Kannada", "Odia", "Malay", "Indonesian",
        "Filipino", "Tagalog", "Romanian", "Hungarian", "Czech", "Slovak",
        "Bulgarian", "Serbian", "Croatian", "Ukrainian", "Belarusian",
        "Lithuanian", "Latvian", "Estonian", "Icelandic", "Slovenian"
    ]
    text_lower = text.lower()
    for lang in known_languages_list:
        if re.search(r'\b' + re.escape(lang.lower()) + r'\b', text_lower):
            languages.append(lang)
    return languages
