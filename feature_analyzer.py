import openai
from typing import Dict, List, Any
import os
import json
from dotenv import load_dotenv
import sys
import argparse

class FeatureAnalyzer:
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()

        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables. Please check your .env file.")

        self.client = openai.OpenAI(api_key=api_key)

        # Configure analysis settings
        self.max_tokens = 4000
        self.model = "gpt-3.5-turbo"
        self.chunk_size = 12000
        self.analysis_cache = {}

        # Features to check via directory structure
        self.directory_features = {
            "already_deployed": ["docker-compose.yml", "kubernetes", "deploy.sh", ".env.production"],
            "has_frontend": ["src/frontend", "public", "index.html", "components", "pages"],
            "has_cicd": [".github/workflows", "jenkins", "gitlab-ci.yml", ".travis.yml"],
            "multiple_environments": [".env.", "config/environments"],
            "uses_containerization": ["dockerfile", "docker-compose", "kubernetes"],
            "uses_iac": ["terraform", "cloudformation", "pulumi", "ansible"],
            "high_availability": ["kubernetes", "docker-swarm", "load-balancer"],
        }

        # Features to analyze via LLM
        self.llm_features = {
            "authentication": {"present": False, "details": [], "improvements": []},
            "realtime_events": {"present": False, "details": [], "improvements": []},
            "storage": {"present": False, "details": [], "improvements": []},
            "caching": {"present": False, "details": [], "improvements": []},
            "ai_implementation": {"present": False, "details": [], "improvements": []},
            "database": {"present": False, "details": [], "improvements": []},
            "microservices": {"present": False, "details": [], "improvements": []},
            "monolith": {"present": False, "details": [], "improvements": []},
            "api_exposed": {"present": False, "details": [], "improvements": []},
            "message_queues": {"present": False, "details": [], "improvements": []},
            "background_jobs": {"present": False, "details": [], "improvements": []},
            "sensitive_data": {"present": False, "details": [], "improvements": []},
            "external_apis": {"present": False, "details": [], "improvements": []}
        }

    def chunk_code_by_files(self, code_content: str) -> List[str]:
        """Split code content into chunks based on file headers and size limits."""
        print("\n[DEBUG] Chunking code content...")
        chunks = []
        current_chunk = []
        current_size = 0

        lines = code_content.split('\n')
        for line_num, line in enumerate(lines):
            line_size = len(line)

            # If adding this line would exceed chunk size, start a new chunk
            if current_size + line_size > self.chunk_size and current_chunk:
                chunks.append('\n'.join(current_chunk))
                current_chunk = []
                current_size = 0

            current_chunk.append(line)
            current_size += line_size

            # When we hit a file header, consider starting a new chunk
            if line.startswith('=' * 48) and current_size > self.chunk_size / 2:
                chunks.append('\n'.join(current_chunk))
                current_chunk = []
                current_size = 0

        # Add the last chunk if it exists
        if current_chunk:
            chunks.append('\n'.join(current_chunk))

        print(f"[DEBUG] Created {len(chunks)} total chunks")
        return chunks

    def analyze_with_llm(self, code_content: str) -> Dict[str, Any]:
        print("\n[ANALYSIS] Starting LLM analysis...")
        code_chunks = self.chunk_code_by_files(code_content)
        if not code_chunks:
            print("[WARNING] No valid code chunks found for analysis!")

        combined_analysis = {
            "authentication": {"present": False, "details": []},
            "realtime_events": {"present": False, "details": []},
            "storage": {"present": False, "details": []},
            "caching": {"present": False, "details": []},
            "ai_implementation": {"present": False, "details": []},
            "database": {"present": False, "details": []},
            "microservices": {"present": False, "details": []},
            "monolith": {"present": False, "details": []},
            "api_exposed": {"present": False, "details": []},
            "message_queues": {"present": False, "details": []},
            "background_jobs": {"present": False, "details": []},
            "sensitive_data": {"present": False, "details": []},
            "external_apis": {"present": False, "details": []}
        }

        prompt = """Analyze the following code snippet and determine if it implements any of these features. For each feature:
1. Indicate if it's present
2. Provide details about the implementation if found
3. Suggest specific improvements or implementations if needed (e.g., "Should implement Redis caching for user sessions" or "Needs S3 bucket for file uploads")

Features to analyze:
1. Authentication (user login, signup, JWT, sessions)
2. Realtime Events (websockets, server-sent events)
3. Storage (file uploads, cloud storage)
4. Caching (Redis, in-memory)
5. AI Implementation (ML models, AI APIs)
6. Database Operations (any data persistence)
7. Microservices Architecture (service separation)
8. Monolithic Architecture (single application)
9. API Endpoints (REST, GraphQL)
11. Message Queues (RabbitMQ, Kafka)
12. Background Jobs (workers, scheduled tasks)
13. Sensitive Data Handling (PII, encryption)
14. External API Dependencies

Return your analysis in this exact JSON format:
{
    "authentication": {"present": false, "details": "", "improvements": ""},
    "realtime_events": {"present": false, "details": "", "improvements": ""},
    "storage": {"present": false, "details": "", "improvements": ""},
    "caching": {"present": false, "details": "", "improvements": ""},
    "ai_implementation": {"present": false, "details": "", "improvements": ""},
    "database": {"present": false, "details": "", "improvements": ""},
    "microservices": {"present": false, "details": "", "improvements": ""},
    "monolith": {"present": false, "details": "", "improvements": ""},
    "api_exposed": {"present": false, "details": "", "improvements": ""},
    "message_queues": {"present": false, "details": "", "improvements": ""},
    "background_jobs": {"present": false, "details": "", "improvements": ""},
    "sensitive_data": {"present": false, "details": "", "improvements": ""},
    "external_apis": {"present": false, "details": "", "improvements": ""}
}"""

        for chunk_num, chunk in enumerate(code_chunks, 1):
            # Check cache first
            cache_key = hash(chunk)
            if cache_key in self.analysis_cache:
                print(f"[CHUNK {chunk_num}] Using cached analysis")
                chunk_analysis = self.analysis_cache[cache_key]
                continue

            chunk_analysis = None
            try:
                print(f"\n[CHUNK {chunk_num}] Processing chunk ({len(chunk)} characters)")

                # Skip small chunks that are just headers
                if len(chunk.strip()) < 100:
                    print(f"[CHUNK {chunk_num}] Skipping small chunk")
                    continue

                print(f"[CHUNK {chunk_num}] Sending to OpenAI API...")

                response = self.client.chat.completions.create(
                    model=self.model,  # Use cheaper model
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a code analysis expert. Analyze the code and return ONLY valid JSON matching the exact format specified. Do not include any additional text or formatting."
                        },
                        {"role": "user", "content": f"{prompt}\n\nCode to analyze:\n{chunk}"}
                    ],
                    temperature=0,
                    response_format={"type": "json_object"}
                )

                raw_response = response.choices[0].message.content
                print(f"[CHUNK {chunk_num}] Raw API response:\n{raw_response}")

                # Parse JSON while preserving details text formatting
                chunk_analysis = json.loads(raw_response)

                # Normalize JSON keys only
                chunk_analysis = {k.strip().lower(): v for k, v in chunk_analysis.items()}

                print(f"[CHUNK {chunk_num}] Parsed JSON: {json.dumps(chunk_analysis, indent=2)}")

                # Validate feature structure
                required_features = ['authentication', 'database', 'caching', 'storage', 'microservices']
                missing_features = [f for f in required_features if f not in chunk_analysis]

                if missing_features:
                    print(f"[CHUNK {chunk_num}] Missing features in response: {missing_features}")
                    print(f"[CHUNK {chunk_num}] Available keys: {list(chunk_analysis.keys())}")
                    continue

                # Validate feature format
                valid = True
                for feature in required_features:
                    if not isinstance(chunk_analysis[feature].get('present'), bool):
                        print(f"[CHUNK {chunk_num}] Invalid format for {feature}")
                        valid = False
                if not valid:
                    continue

                # Merge results
                for feature in combined_analysis:
                    if chunk_analysis[feature]["present"]:
                        combined_analysis[feature]["present"] = True
                        combined_analysis[feature]["details"].append(
                            chunk_analysis[feature]["details"]
                        )

                # Cache the successful response
                self.analysis_cache[cache_key] = chunk_analysis

            except json.JSONDecodeError as e:
                print(f"[CHUNK {chunk_num}] JSON DECODE ERROR: {str(e)}")
                print(f"[CHUNK {chunk_num}] Invalid JSON content: {raw_response}")
            except KeyError as e:
                print(f"[CHUNK {chunk_num}] KEY ERROR: {str(e)}")
                if chunk_analysis:
                    print(f"[CHUNK {chunk_num}] Available features: {list(chunk_analysis.keys())}")
            except Exception as e:
                print(f"[CHUNK {chunk_num}] UNEXPECTED ERROR: {str(e)}")
                print(f"[CHUNK {chunk_num}] Response dump: {vars(response)}")

        # Clean up details
        print("\n[ANALYSIS] Combining results...")
        for feature in combined_analysis:
            if combined_analysis[feature]["details"]:
                combined_analysis[feature]["details"] = "\n".join(
                    set(combined_analysis[feature]["details"])
                )
            else:
                combined_analysis[feature]["details"] = "Not found"

        return combined_analysis

    def analyze_project(self, directory_content: str, code_content: str) -> Dict[str, Any]:
        # Get directory analysis using traditional method
        dir_features = self.analyze_directory_structure(directory_content)

        # Get intelligent code analysis using LLM
        llm_analysis = self.analyze_with_llm(code_content)

        # Combine the results
        combined_features = {}
        for feature in self.features.keys():
            dir_result = dir_features.get(feature, False)
            llm_result = llm_analysis.get(feature, {}).get("present", False)

            combined_features[feature] = {
                "present": dir_result or llm_result,
                "directory_indicators": dir_result,
                "code_analysis": llm_analysis.get(feature, {})
            }

        return {
            'directory_analysis': dir_features,
            'llm_analysis': llm_analysis,
            'combined_analysis': combined_features
        }

    def analyze_directory_structure(self, directory_content: str) -> Dict[str, bool]:
        """Analyze directory structure for infrastructure and deployment patterns."""
        found_features = {feature: False for feature in self.directory_features}

        # Convert to lowercase for case-insensitive matching
        directory_content = directory_content.lower()

        for feature, patterns in self.directory_features.items():
            for pattern in patterns:
                if pattern.lower() in directory_content:
                    found_features[feature] = True
                    break

        return found_features

    def analyze_code_content(self, code_content):
        found_features = {feature: False for feature in self.features}

        # Convert to lowercase for case-insensitive matching
        code_content = code_content.lower()

        # Check each feature's code patterns
        for feature, patterns in self.features.items():
            for pattern in patterns['code']:
                if pattern.lower() in code_content:
                    found_features[feature] = True
                    break

        return found_features

if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(description='Analyze repository features')
        parser.add_argument('repo', help='Repository in format owner/repo')
        args = parser.parse_args()

        # Convert repo name to file format and construct paths
        base_filename = args.repo.replace('/', '_')
        temp_dir = "temp"
        directory_file = os.path.join(temp_dir, f"{base_filename}_directory_structure.txt")
        code_file = os.path.join(temp_dir, f"{base_filename}_code_content.txt")

        # Check if files exist
        if not os.path.exists(directory_file):
            print(f"Error: Directory structure file not found: {directory_file}")
            sys.exit(1)
        if not os.path.exists(code_file):
            print(f"Error: Code content file not found: {code_file}")
            sys.exit(1)

        # Read directory structure
        with open(directory_file, 'r', encoding='utf-8') as f:
            directory_content = f.read()
            print(f"Read directory structure ({len(directory_content)} characters)")

        # Read code content
        with open(code_file, 'r', encoding='utf-8') as f:
            code_content = f.read()
            print(f"Read code content ({len(code_content)} characters)")

        # Run analysis
        analyzer = FeatureAnalyzer()
        dir_results = analyzer.analyze_directory_structure(directory_content)
        code_results = analyzer.analyze_with_llm(code_content)

        # Combine results
        combined_results = {
            "infrastructure_analysis": dir_results,
            "code_analysis": code_results
        }

        # Save results in temp directory
        results_file = os.path.join(temp_dir, f"{base_filename}_analysis_results.json")
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(combined_results, f, indent=2)
            print(f"\nSaved results to {results_file}")

        print("\n=== Analysis Results ===")
        print("\nInfrastructure Features:")
        for feature, present in dir_results.items():
            status = "✓" if present else "✗"
            print(f"{feature.replace('_', ' ').title()}: {status}")

        print("\nCode Features:")
        for feature, data in code_results.items():
            status = "✓" if data["present"] else "✗"
            print(f"\n{feature.replace('_', ' ').title()}: {status}")
            if data["present"]:
                print(f"Details: {data['details']}")
            if data.get("improvements"):
                print(f"Suggested Improvements: {data['improvements']}")

    except Exception as e:
        print(f"[ERROR] {str(e)}")
        exit(1)
