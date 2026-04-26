"""
Service de parsing de CV (PDF, DOCX, TXT)
Extraction de texte et de données structurées depuis des fichiers CV
"""

import re
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class CVParser:
    """Parse CV files and extract structured information"""
    
    def __init__(self):
        self.skill_keywords = [
            # Programming Languages
            'Python', 'Java', 'Java 8', 'Java 11', 'Java 17', 'JavaScript', 'TypeScript', 
            'C++', 'C#', 'C', 'PHP', 'Ruby', 'Go', 'Rust', 'Swift', 'Kotlin', 'Dart',
            'Scala', 'R', 'MATLAB', 'Perl', 'Shell', 'Bash', 'PowerShell', 'VB.NET',
            'Objective-C', 'Groovy', 'Clojure', 'Haskell', 'Elixir', 'Erlang',
            
            # Frameworks & Libraries - Web
            'React', 'React Native', 'Angular', 'Vue', 'Vue.js', 'Svelte', 'Next.js', 'Nuxt.js',
            'Node.js', 'Express', 'Express.js', 'Nest.js', 'Koa', 'Fastify',
            'Django', 'Flask', 'FastAPI', 'Pyramid', 'Tornado',
            'Spring', 'Spring Boot', 'Spring MVC', 'Spring Cloud', 'Spring Security',
            'Laravel', 'Symfony', 'CodeIgniter', 'Yii', 'CakePHP',
            'Rails', 'Ruby on Rails', 'Sinatra',
            'ASP.NET', 'ASP.NET Core', '.NET', '.NET Core', 'Entity Framework',
            'jQuery', 'Bootstrap', 'Tailwind CSS', 'Material-UI', 'Ant Design',
            'Redux', 'MobX', 'Vuex', 'Pinia', 'Recoil',
            
            # Frameworks & Libraries - Mobile
            'Flutter', 'React Native', 'Ionic', 'Xamarin', 'Cordova', 'PhoneGap',
            'SwiftUI', 'UIKit', 'Jetpack Compose',
            
            # Frameworks & Libraries - AI/ML
            'TensorFlow', 'PyTorch', 'Keras', 'Scikit-learn', 'XGBoost', 'LightGBM',
            'Pandas', 'NumPy', 'SciPy', 'Matplotlib', 'Seaborn', 'Plotly',
            'OpenCV', 'NLTK', 'spaCy', 'Hugging Face', 'Transformers',
            'Caffe', 'Theano', 'MXNet', 'JAX',
            
            # Databases - SQL
            'SQL', 'MySQL', 'PostgreSQL', 'Oracle', 'Oracle DB', 'SQL Server', 'MariaDB',
            'SQLite', 'DB2', 'Sybase', 'T-SQL', 'PL/SQL',
            
            # Databases - NoSQL
            'MongoDB', 'Redis', 'Cassandra', 'CouchDB', 'Neo4j', 'DynamoDB',
            'Elasticsearch', 'Solr', 'Couchbase', 'RethinkDB', 'ArangoDB',
            'Firebase', 'Firebase Realtime Database', 'Firestore',
            
            # Cloud Platforms
            'AWS', 'Amazon Web Services', 'Azure', 'Microsoft Azure', 'GCP', 'Google Cloud',
            'AWS Lambda', 'EC2', 'S3', 'RDS', 'CloudFormation', 'CloudWatch',
            'Azure Functions', 'Azure DevOps', 'Google Cloud Functions', 'Cloud Run',
            'Heroku', 'DigitalOcean', 'Linode', 'IBM Cloud', 'Oracle Cloud',
            
            # DevOps & CI/CD
            'Docker', 'Kubernetes', 'K8s', 'Helm', 'OpenShift', 'Rancher',
            'Jenkins', 'GitLab CI', 'GitHub Actions', 'Travis CI', 'CircleCI',
            'Azure Pipelines', 'Bamboo', 'TeamCity', 'ArgoCD', 'Flux',
            'Terraform', 'Ansible', 'Chef', 'Puppet', 'SaltStack', 'Vagrant',
            'CI/CD', 'DevOps', 'GitOps', 'Infrastructure as Code', 'IaC',
            
            # Version Control & Collaboration
            'Git', 'GitHub', 'GitLab', 'Bitbucket', 'SVN', 'Mercurial', 'Perforce',
            
            # Build Tools & Package Managers
            'Maven', 'Gradle', 'Ant', 'npm', 'Yarn', 'pnpm', 'pip', 'Poetry',
            'Composer', 'Bundler', 'NuGet', 'Webpack', 'Vite', 'Rollup', 'Parcel',
            'Gulp', 'Grunt', 'Make', 'CMake', 'Bazel',
            
            # Testing
            'JUnit', 'TestNG', 'Mockito', 'Jest', 'Mocha', 'Chai', 'Jasmine',
            'Cypress', 'Selenium', 'Playwright', 'Puppeteer', 'WebDriverIO',
            'PyTest', 'unittest', 'RSpec', 'PHPUnit', 'NUnit', 'xUnit',
            'Cucumber', 'JBehave', 'SpecFlow', 'Postman', 'SoapUI', 'JMeter',
            'k6', 'Locust', 'Gatling',
            
            # Quality & Code Analysis
            'SonarQube', 'SonarCloud', 'ESLint', 'Prettier', 'TSLint', 'Pylint',
            'Black', 'Flake8', 'Checkstyle', 'PMD', 'FindBugs', 'SpotBugs',
            'CodeClimate', 'Coverity',
            
            # Monitoring & Logging
            'Prometheus', 'Grafana', 'ELK', 'Elasticsearch', 'Logstash', 'Kibana',
            'Datadog', 'New Relic', 'AppDynamics', 'Splunk', 'Nagios', 'Zabbix',
            'Jaeger', 'Zipkin', 'OpenTelemetry',
            
            # Message Queues & Streaming
            'Kafka', 'Apache Kafka', 'RabbitMQ', 'ActiveMQ', 'ZeroMQ', 'NATS',
            'Redis Pub/Sub', 'Amazon SQS', 'Amazon SNS', 'Azure Service Bus',
            'Google Pub/Sub', 'Pulsar',
            
            # Big Data & ETL
            'Hadoop', 'Spark', 'Apache Spark', 'Hive', 'Pig', 'HBase', 'Flink',
            'Storm', 'Samza', 'Presto', 'Drill', 'Impala',
            'Airflow', 'Apache Airflow', 'Luigi', 'Prefect', 'Dagster',
            'Talend', 'Informatica', 'Apache NiFi', 'Pentaho',
            
            # Data Visualization & BI
            'Tableau', 'Power BI', 'Looker', 'QlikView', 'Qlik Sense', 'Metabase',
            'Superset', 'Redash', 'D3.js', 'Chart.js', 'Highcharts',
            
            # API & Web Services
            'REST', 'REST API', 'RESTful', 'GraphQL', 'gRPC', 'SOAP', 'WebSocket',
            'API Gateway', 'Swagger', 'OpenAPI', 'Postman', 'Insomnia',
            
            # Architecture & Design
            'Microservices', 'SOA', 'Event-Driven Architecture', 'CQRS', 'Event Sourcing',
            'Domain-Driven Design', 'DDD', 'Clean Architecture', 'Hexagonal Architecture',
            'MVC', 'MVVM', 'MVP', 'Design Patterns',
            
            # Modeling & Documentation
            'UML', 'SysML', 'BPMN', 'ArchiMate', 'C4 Model',
            'Magicdraw', 'Enterprise Architect', 'Visio', 'Draw.io', 'Lucidchart',
            'PlantUML', 'Mermaid',
            
            # Methodologies
            'Agile', 'Scrum', 'Kanban', 'XP', 'Lean', 'SAFe', 'Waterfall',
            'Test-Driven Development', 'TDD', 'Behavior-Driven Development', 'BDD',
            
            # Project Management & Collaboration
            'Jira', 'Confluence', 'Trello', 'Asana', 'Monday.com', 'ClickUp',
            'Azure DevOps', 'ServiceNow', 'Slack', 'Microsoft Teams',
            
            # IDEs & Editors
            'IntelliJ IDEA', 'Eclipse', 'NetBeans', 'PyCharm', 'WebStorm', 'PhpStorm',
            'Visual Studio', 'VS Code', 'Visual Studio Code', 'Sublime Text', 'Atom',
            'Android Studio', 'Xcode', 'Rider', 'DataGrip',
            
            # Security
            'OAuth', 'OAuth2', 'JWT', 'SAML', 'OpenID Connect', 'LDAP', 'Active Directory',
            'Keycloak', 'Okta', 'Auth0', 'SSL/TLS', 'PKI', 'Penetration Testing',
            'OWASP', 'Vault', 'HashiCorp Vault',
            
            # Networking
            'TCP/IP', 'HTTP', 'HTTPS', 'DNS', 'Load Balancing', 'Nginx', 'Apache',
            'HAProxy', 'Traefik', 'Envoy', 'Istio', 'Service Mesh',
            
            # Operating Systems
            'Linux', 'Unix', 'Ubuntu', 'CentOS', 'Red Hat', 'RHEL', 'Debian',
            'Windows', 'Windows Server', 'MacOS', 'FreeBSD',
            
            # Containers & Orchestration  
            'Container', 'Containerization', 'Docker Compose', 'Docker Swarm',
            'Podman', 'LXC', 'LXD',
            
            # Data Science & Analytics
            'Machine Learning', 'Deep Learning', 'NLP', 'Natural Language Processing',
            'Computer Vision', 'Data Science', 'Data Analysis', 'Data Mining',
            'Big Data', 'Statistical Analysis', 'Predictive Analytics',
            'Feature Engineering', 'Model Deployment', 'MLOps', 'MLflow',
            
            # Artifact Management
            'Nexus', 'Artifactory', 'JFrog', 'npm Registry', 'Docker Registry',
            
            # Others
            'Blockchain', 'Ethereum', 'Solidity', 'Web3', 'Smart Contracts',
            'IoT', 'MQTT', 'CoAP', 'Edge Computing',
            'Serverless', 'FaaS', 'Lambda Functions',
            'WebRTC', 'WebAssembly', 'PWA', 'Progressive Web Apps'
        ]
    
    def parse_text_file(self, content: bytes) -> str:
        """Parse text file"""
        try:
            # Try UTF-8 first
            return content.decode('utf-8')
        except UnicodeDecodeError:
            # Fallback to latin-1
            try:
                return content.decode('latin-1')
            except:
                return content.decode('utf-8', errors='ignore')
    
    def parse_pdf_with_ocr(self, content: bytes) -> str:
        """Parse scanned PDF using OCR (Tesseract)"""
        try:
            import pytesseract
            from pdf2image import convert_from_bytes
            from io import BytesIO
            import os
            
            # Configure Tesseract path
            tesseract_paths = [
                r'C:\Users\wdaoud\AppData\Local\Programs\Tesseract-OCR\tesseract.exe',
                r'C:\Program Files\Tesseract-OCR\tesseract.exe',
                r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
            ]
            
            for path in tesseract_paths:
                if os.path.exists(path):
                    pytesseract.pytesseract.tesseract_cmd = path
                    break
            
            # Configure Poppler path
            poppler_paths = [
                r'C:\Users\wdaoud\AppData\Local\Programs\poppler\Library\bin',
                r'C:\Program Files\poppler\Library\bin',
                r'C:\poppler\Library\bin',
            ]
            
            poppler_path = None
            for path in poppler_paths:
                if os.path.exists(path):
                    poppler_path = path
                    break
            
            # Convert PDF to images
            if poppler_path:
                images = convert_from_bytes(content, dpi=150, poppler_path=poppler_path)
            else:
                # Try without explicit path (if in system PATH)
                images = convert_from_bytes(content, dpi=150)
            
            # Extract text from each page
            text = ""
            for img in images:
                page_text = pytesseract.image_to_string(img, lang='eng')
                text += page_text + "\n"
            
            return text.strip()
            
        except ImportError as e:
            logger.warning(f"OCR libraries not installed: {e}")
            return ""
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            return ""
    
    def parse_pdf(self, content: bytes) -> str:
        """Parse PDF file using PyMuPDF with OCR fallback for scanned PDFs"""
        # Try PyMuPDF first (better extraction)
        try:
            import fitz  # PyMuPDF
            from io import BytesIO
            
            pdf_file = BytesIO(content)
            doc = fitz.open(stream=pdf_file, filetype="pdf")
            
            text = ""
            for page in doc:
                text += page.get_text() + "\n"
            
            doc.close()
            
            # If we got good text, return it
            if text and len(text.strip()) > 50:
                return text
            
            # If text is too short, PDF might be scanned - try OCR
            logger.info("PDF appears to be scanned (no text found), trying OCR...")
            ocr_text = self.parse_pdf_with_ocr(content)
            if ocr_text and len(ocr_text.strip()) > 50:
                return ocr_text
            
            return text  # Return whatever we got
            
        except ImportError:
            logger.debug("PyMuPDF not installed, trying PyPDF2")
        except Exception as e:
            logger.debug(f"PyMuPDF extraction failed: {e}, trying PyPDF2")
        
        # Fallback to PyPDF2
        try:
            import PyPDF2
            from io import BytesIO
            
            pdf_file = BytesIO(content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text = ""
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            
            # If text is too short, try OCR
            if len(text.strip()) < 50:
                logger.info("PDF appears to be scanned, trying OCR...")
                ocr_text = self.parse_pdf_with_ocr(content)
                if ocr_text and len(ocr_text.strip()) > 50:
                    return ocr_text
            
            return text
            
        except ImportError:
            logger.warning("Neither PyMuPDF nor PyPDF2 installed. Install with: pip install PyMuPDF PyPDF2")
            return ""
        except Exception as e:
            logger.error(f"Error parsing PDF with both libraries: {e}")
            return ""
    
    def parse_docx(self, content: bytes) -> str:
        """Parse DOCX file"""
        try:
            import docx
            from io import BytesIO
            
            doc_file = BytesIO(content)
            doc = docx.Document(doc_file)
            
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            return text
        except ImportError:
            logger.warning("python-docx not installed. Install with: pip install python-docx")
            return ""
        except Exception as e:
            logger.error(f"Error parsing DOCX: {e}")
            return ""
    
    def extract_skills(self, text: str) -> List[str]:
        """Extract skills from text using keyword matching"""
        found_skills = []
        text_lower = text.lower()
        
        for skill in self.skill_keywords:
            # Case-insensitive search with word boundaries
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.append(skill)
        
        return sorted(list(set(found_skills)))
    
    def extract_email(self, text: str) -> Optional[str]:
        """Extract email from text"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(email_pattern, text)
        return match.group(0) if match else None
    
    def extract_phone(self, text: str) -> Optional[str]:
        """Extract phone number from text"""
        # French phone patterns
        phone_patterns = [
            r'\b(?:0|\+33)[1-9](?:[\s.-]?\d{2}){4}\b',  # French format
            r'\b\d{10}\b',  # 10 digits
            r'\+\d{2,3}[\s.-]?\d{9,10}\b'  # International
        ]
        
        for pattern in phone_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        
        return None
    
    def extract_years_of_experience(self, text: str) -> Optional[float]:
        """Extract years of experience from text"""
        # Patterns for experience mentions
        patterns = [
            r'(\d+)\s*(?:ans?|years?)\s*(?:d\'|de|of)?\s*(?:expérience|experience)',
            r'(?:expérience|experience)\s*(?:de|of)?\s*(\d+)\s*(?:ans?|years?)',
            r'(\d+)\+?\s*(?:ans?|years?)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                try:
                    return float(match.group(1))
                except:
                    pass
        
        return None
    
    def _identify_sections(self, text: str) -> Dict[str, List[str]]:
        """Identify CV sections (Experience, Education, etc.) with improved logic"""
        sections = {
            'experience': [],
            'education': [],
            'other': []
        }
        
        lines = text.split('\n')
        current_section = 'other'
        
        # Section headers patterns
        exp_patterns = ['expérience', 'experience', 'parcours professionnel', 'professional experience', 'emplois']
        edu_patterns = ['formation', 'education', 'diplôme', 'diplomas', 'études', 'academic']
        
        for line in lines:
            line_lower = line.lower().strip()
            
            # Check if this is a section header
            if any(pattern in line_lower for pattern in exp_patterns) and len(line_lower) < 50:
                current_section = 'experience'
                continue
            elif any(pattern in line_lower for pattern in edu_patterns) and len(line_lower) < 50:
                current_section = 'education'
                continue
            
            # Add non-empty lines to current section
            if line.strip() and len(line.strip()) > 5:
                sections[current_section].append(line.strip())
        
        return sections
    
    def extract_education(self, text: str) -> List[str]:
        """Extract education/diplomas from text using section detection"""
        sections = self._identify_sections(text)
        education = []
        
        # First, try from education section
        education_keywords = [
            'master', 'bachelor', 'licence', 'doctorat', 'phd', 'mba',
            'bts', 'dut', 'diplôme', 'degree', 'ingénieur',
            'university', 'université', 'école', 'school'
        ]
        
        # Prioritize education section
        for line in sections['education']:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in education_keywords):
                if len(line) > 10 and len(line) < 200:
                    education.append(line)
        
        # If nothing found, search in other sections (but exclude experience section)
        if not education:
            for line in sections['other']:
                line_lower = line.lower()
                if any(keyword in line_lower for keyword in education_keywords):
                    if len(line) > 10 and len(line) < 200:
                        education.append(line)
        
        return education[:5]  # Limit to 5 entries
    
    def extract_job_titles(self, text: str) -> List[str]:
        """Extract job titles from text using section detection"""
        sections = self._identify_sections(text)
        job_titles = []
        
        # Job title keywords
        title_keywords = [
            'developer', 'développeur', 'engineer', 'analyst', 'analyste',
            'manager', 'directeur', 'consultant', 'architect', 'architecte',
            'lead', 'senior', 'junior', 'data scientist', 'devops',
            'designer', 'chef de projet', 'responsable', 'coordinateur'
        ]
        
        # Extract from experience section only
        for line in sections['experience']:
            line_lower = line.lower()
            # Check if line contains job title keyword
            if any(keyword in line_lower for keyword in title_keywords):
                # Exclude lines that are clearly not job titles
                if not any(x in line_lower for x in ['formation', 'diplôme', 'université', 'école']):
                    if 5 < len(line) < 150:
                        job_titles.append(line)
        
        # If nothing found in experience, try other sections
        if not job_titles:
            for line in sections['other']:
                line_lower = line.lower()
                if any(keyword in line_lower for keyword in title_keywords):
                    if not any(x in line_lower for x in ['formation', 'diplôme', 'université', 'école']):
                        if 5 < len(line) < 150:
                            job_titles.append(line)
        
        return job_titles[:5]  # Limit to 5
    
    def parse_cv(self, filename: str, content: bytes) -> Dict:
        """
        Parse CV file and extract structured data
        
        Args:
            filename: Name of the file
            content: File content as bytes
            
        Returns:
            Dictionary with extracted CV data
        """
        # Extract text based on file type
        text = ""
        file_ext = filename.lower().split('.')[-1]
        
        if file_ext == 'txt':
            text = self.parse_text_file(content)
        elif file_ext == 'pdf':
            text = self.parse_pdf(content)
        elif file_ext in ['docx', 'doc']:
            text = self.parse_docx(content)
        else:
            text = self.parse_text_file(content)  # Try as text
        
        if not text:
            return {
                "success": False,
                "error": f"Could not extract text from {file_ext} file",
                "text": "",
                "data": {}
            }
        
        # Extract structured data
        skills = self.extract_skills(text)
        sections = self._identify_sections(text)
        education = self.extract_education(text)
        job_titles = self.extract_job_titles(text)
        years_exp = self.extract_years_of_experience(text)
        email = self.extract_email(text)
        phone = self.extract_phone(text)
        
        # Extract experiences from experience section
        experiences = []
        if sections['experience']:
            # Group lines into experience entries (entries separated by date patterns or multiple empty lines)
            current_exp = []
            for line in sections['experience']:
                # If line looks like a job title or company, start new entry
                if len(current_exp) > 0 and (
                    re.search(r'\d{4}', line) or  # Contains year
                    len(line) < 80  # Short line (likely title)
                ):
                    if current_exp:
                        experiences.append(' '.join(current_exp))
                        current_exp = []
                
                if len(line) > 20:  # Meaningful content
                    current_exp.append(line)
            
            # Add last experience
            if current_exp:
                experiences.append(' '.join(current_exp))
        
        return {
            "success": True,
            "text": text,
            "data": {
                "skills": skills,
                "experiences": experiences[:3] if experiences else ["Aucune expérience détectée"],
                "job_titles": job_titles if job_titles else ["Aucun poste détecté"],
                "education": education if education else ["Aucune formation détectée"],
                "years_of_experience": years_exp,
                "email": email,
                "phone": phone,
                "extracted_skills_count": len(skills)
            }
        }


# Helper function for easy CV parsing
async def extract_cv_data(content: bytes, filename: str) -> Dict:
    """
    Extract CV data from file content
    
    Args:
        content: File content as bytes
        filename: Name of the file
        
    Returns:
        Dictionary with CV data including skills, experience, education, etc.
    """
    parser = CVParser()
    result = parser.parse_cv(filename, content)
    
    if not result.get("success"):
        return {
            "full_text": "",
            "skills": [],
            "experience": [],
            "job_titles": [],
            "education": [],
            "years_of_experience": None
        }
    
    data = result.get("data", {})
    
    return {
        "full_text": result.get("text", ""),
        "skills": data.get("skills", []),
        "experience": data.get("experiences", []),
        "job_titles": data.get("job_titles", []),
        "education": data.get("education", []),
        "years_of_experience": data.get("years_of_experience")
    }

