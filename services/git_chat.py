from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langchain.agents.react.agent import create_react_agent

from loguru import logger as log

from config import Config
from services.git_diff_summarizer import GitDiffSummarizer
from services.input_validator import InputValidator


@tool
async def analyze_git_diff(project_path: str, source_branch: str, target_branch: str, output_file: str, model: str = "llama3.2", ollama_url: str = "http://localhost:11434") -> str:
    """
    Run a complete Git diff analysis using the GitDiffSummarizer.
    
    Args:
        project_path: Path to the Git project directory
        source_branch: Name of the local/feature branch to compare
        target_branch: Name of the master/base branch to compare against
        output_file: Path to the output file for the summary
        model: Ollama model to use (default: llama3.2)
        ollama_url: Ollama server URL (default: http://localhost:11434)
    
    Returns:
        Success message with output file location
    """
    try:
        # Create configuration
        InputValidator.check_git_availability()
        InputValidator.check_ollama_availability(ollama_url)

        project_path = InputValidator.validate_project_path(project_path)
        output_file = InputValidator.validate_output_file(output_file)
        source_branch = InputValidator.validate_branch_name(source_branch)
        target_branch = InputValidator.validate_branch_name(target_branch)

        config = Config(
            project_path=project_path,
            source_branch=source_branch,
            target_branch=target_branch,
            output_file=output_file,
            ollama_model=model,
            ollama_url=ollama_url
        )

        # Run the summarizer
        summarizer = GitDiffSummarizer(config)
        await summarizer.run()
        return f"✅ Git diff analysis completed successfully! Results saved to: {output_file}"
        
    except Exception as e:
        return f"❌ Error running Git diff analysis: {str(e)}"


def create_git_diff_chat_prompt():
    """Create the system prompt for the Git diff summarizer assistant."""
    return """You are a Git Diff Summarizer Assistant - an AI tool designed to help developers analyze changes between Git branches before merging.

YOUR PRIMARY PURPOSE:
🎯 Help users gather the required information to run git diff analysis
� Use the analyze_git_diff tool to generate comprehensive branch comparison summaries
📋 Guide users through providing the necessary parameters for analysis

REQUIRED INFORMATION TO COLLECT:
1. Project Path: The path to the Git repository directory
2. Local Branch: The feature/working branch to analyze
3. Target Branch: The branch to merge into (usually main/master)
4. Output File: Where to save the analysis report

WORKFLOW:
1. Greet the user and explain the purpose
2. Ask for missing required information in a conversational way
3. Once you have all parameters, run the analyze_git_diff tool
4. Provide the results and any recommendations

PERSONALITY:
- Professional and focused
- Helpful in gathering information
- Clear about what information is needed
- Efficient and direct

EXAMPLE INTERACTIONS:
- If user says "analyze my branch": Ask for project path, branch names, and output file
- If user provides partial info: Ask for the missing pieces
- Always confirm the parameters before running analysis

Your goal is to make it easy for developers to get comprehensive git diff summaries before merging their branches."""



class GitDiffChat:
    """Interactive Git diff summarizer assistant powered by LangChain and Ollama."""
    
    def __init__(self, model: str = "llama3.2", ollama_url: str = "http://localhost:11434"):
        self.model = model
        self.ollama_url = ollama_url
        self.llm = self._create_llm()
        self.agent = self._create_agent()
        
        # Track information gathering state
        self.session_data = {
            "project_path": None,
            "source_branch": None,
            "target_branch": None,
            "output_file": None
        }
    
    def _create_llm(self):
        """Create and configure the LLM instance."""
        return ChatOllama(
            model=self.model,
            base_url=self.ollama_url,
            temperature=0.1,
            timeout=300,
            num_predict=2048,
        )
    
    def _create_agent(self):
        """Create the reactive agent with tools."""

        return create_react_agent(
            self.llm,
            tools=[analyze_git_diff],
            prompt=create_git_diff_chat_prompt(),
        )

    async def chat(self, user_input: str) -> str:
        """Process user input and return teacher response."""
        try:
            result = await self.agent.ainvoke({
                "messages": [HumanMessage(content=user_input)],
            })

            # Extract the final response
            if result and "messages" in result:
                # Get the last message which should be the assistant's response
                last_message = result["messages"][-1]
                return last_message.content if hasattr(last_message, 'content') else str(last_message)
            
            return "I'm sorry, I couldn't process your request. Please try again."
            
        except Exception as e:
            log.error(f"Git Diff Chat error: {e}")
            return f"I encountered an error: {str(e)}. Please try rephrasing your question."
    
    async def start_interactive_session(self):
        """Start an interactive session focused on git diff analysis."""
        print("\n" + "="*60)
        print("RevAI Interactive Mode - Git Diff Analysis")
        print("="*60)
        print("\nWelcome! I help you analyze changes between Git branches before merging.")
        print("I'll gather the information needed and generate a comprehensive summary.")
        print("\nType 'exit', 'quit', or 'bye' to end the session.")
        print("Type 'help' for examples and guidance.")
        print("-" * 60)
        
        # Start with initial prompt
        initial_prompt = """
Hello! I'm here to help you analyze the differences between your Git branches before merging.

To generate a comprehensive summary, I need the following information:
🔹 Project path (Git repository directory)
🔹 Local branch (your feature/working branch)
🔹 Target branch (branch you want to merge into, e.g., main/master)
🔹 Output file (where to save the analysis report)

You can provide this information in any order, or just tell me what you'd like to analyze!
        """
        print(initial_prompt)
        
        while True:
            try:
                user_input = input("\n💬 You: ").strip()
                
                if not user_input:
                    continue
                
                # Check for exit commands
                if user_input.lower() in ['exit', 'quit', 'bye', 'q']:
                    print("\n👋 Chat session ended. Happy merging! 🚀")
                    break
                
                # Help command
                if user_input.lower() == 'help':
                    self._show_help()
                    continue
                
                # Process input and get response
                print("\n🤖 Chat: ", end="")
                response = await self.chat(user_input)
                print(response)
                
            except KeyboardInterrupt:
                print("\n\n👋 Session interrupted. Thanks for using RevAI!")
                break
            except Exception as e:
                log.error(f"Interactive session error: {e}")
                print(f"\n❌ Sorry, I encountered an error: {str(e)}")
                print("Please try again or type 'exit' to quit.")
    
    @staticmethod
    def _show_help():
        """Show help examples for git diff analysis."""
        print("\nRevAI Interactive Help:")
        print("\nQuick Start Examples:")
        print("  - 'Analyze my feature-branch against main in /home/user/myproject'")
        print("  - 'Compare develop with master, save to summary.md'")
        print("  - 'I want to check my-feature branch before merging to main'")
        
        print("\nRequired Information:")
        print("  🔹 Project path: '/path/to/your/git/repository'")
        print("  🔹 Local branch: 'feature-branch', 'develop', 'my-feature'")
        print("  🔹 Target branch: 'main', 'master', 'staging'")
        print("  🔹 Output file: 'summary.md', 'analysis.txt', 'report.md'")
        
        print("\n💡 Just provide the information in any order and I'll help you generate the analysis!")
