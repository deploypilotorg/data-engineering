import openai
from typing import Dict, List, Any
import os
import json
from dotenv import load_dotenv

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
            "database": {"present": False, "details": []},
            "caching": {"present": False, "details": []},
            "storage": {"present": False, "details": []},
            "microservices": {"present": False, "details": []}
        }

        prompt = """Analyze the following code snippet and determine if it implements any of these features:
1. Authentication (user login, signup, JWT, sessions, etc.)
2. Database operations (any kind of data persistence)
3. Caching mechanisms (Redis, in-memory, etc.)
4. Storage solutions (file uploads, cloud storage, etc.)
5. Microservices architecture (API gateways, message queues, etc.)

Return your analysis in this exact JSON format:
{
    "authentication": {"present": false, "details": ""},
    "database": {"present": false, "details": ""},
    "caching": {"present": false, "details": ""},
    "storage": {"present": false, "details": ""},
    "microservices": {"present": false, "details": ""}
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

    def analyze_directory_structure(self, directory_content):
        found_features = {feature: False for feature in self.features}

        # Convert to lowercase for case-insensitive matching
        directory_content = directory_content.lower()

        # Check each feature's file patterns
        for feature, patterns in self.features.items():
            for pattern in patterns['files']:
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
        # Read code content
        with open('code_content.txt', 'r', encoding='utf-8') as f:
            code_content = f.read()
            print(f"Read {len(code_content)} characters from code_content.txt")

        # Run analysis
        analyzer = FeatureAnalyzer()
        results = analyzer.analyze_with_llm(code_content)

        print("\n=== Analysis Results ===")
        for feature, data in results.items():
            status = "✓" if data["present"] else "✗"
            print(f"\n{feature.capitalize()}: {status}")
            if data["present"]:
                print(f"Details: {data['details']}")

        # Save results
        with open('analysis_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
            print("\nSaved results to analysis_results.json")

    except Exception as e:
        print(f"[ERROR] {str(e)}")
        exit(1)
