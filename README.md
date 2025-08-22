# CV Parser using AI

*Developed by [@cristina-marina1407](https://github.com/cristina-marina1407) 
and [@catalinamanolache](https://github.com/catalinamanolache)*

This project was developed during the final hackathon of the Azure AI 
Summer School.

### Overview
This CV Parser uses AI to analyze and rank candidates based on their CVs. 
It extracts key information such as name, email, education, skills and 
experience and matches it against job requirements to provide a score and 
ranking. This score can be used by HR afterwards. The system leverages 
Azure OpenAI services for intelligent text analysis and information 
extraction, with PyPDF2 for document processing and regex fallback methods.

#### 1. Configuration Management
The system starts by loading Azure OpenAI credentials from environment 
variables (.env file) ensuring secure API key management. It initializes 
the Azure OpenAI client with proper authentication and API versioning.

#### 2. Data Structures
**CompanyRequirements**: Defines job position criteria including required 
skills, education levels, keywords and scoring weights for different 
evaluation categories.

**CandidateProfile**: Stores extracted candidate information including 
personal details, qualifications, skills and calculated scores.

#### 3. CVParser Class
The core parsing engine that handles CV text extraction and analysis:

- **Text Extraction**: Uses PyPDF2 to extract raw text from PDF documents
- **AI-Powered Analysis**: Leverages Azure OpenAI to intelligently parse 
  CV content and extract structured information
- **Fallback Methods**: Implements regex-based extraction when AI services 
  are unavailable or fail
- **Name Extraction**: Advanced pattern matching that filters out university 
  names and company names to identify actual candidate names
- **Email Detection**: Validates and extracts email addresses while 
  filtering generic examples
- **Education Level Detection**: Identifies highest education level using 
  comprehensive regex patterns
- **Skills Matching**: Cross-references CV content with required technical 
  skills
- **Experience Calculation**: Extracts years of experience using multiple 
  pattern recognition strategies

#### 4. CandidateScorer Class
Implements the scoring algorithm that evaluates candidates:

- **Education Scoring**: Assigns points based on education level hierarchy
- **Skills Assessment**: Evaluates technical skills against job requirements
- **Experience Weighting**: Scores professional experience with caps to 
  prevent overvaluation
- **Keyword Matching**: Bonus points for industry-specific terminology
- **Weighted Combination**: Combines all factors using configurable weights

#### 5. Interactive Interface
The main function provides a user-friendly command-line interface:
- Position selection from predefined job requirements
- Dynamic folder path input for CV processing
- Real-time processing feedback
- Automated report generation with timestamps
