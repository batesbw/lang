import getpass
import os
from dotenv import load_dotenv
from langchain.agents import AgentType, initialize_agent
from langchain_anthropic import ChatAnthropic
from weather_tool import create_weather_tool

# Load environment variables from .env file if it exists
load_dotenv()


def _set_env(key: str):
    """Helper function to set environment variables if not already set."""
    if key not in os.environ:
        os.environ[key] = getpass.getpass(f"{key}: ")


class WeatherAgent:
    """A LangChain agent that can check weather for cities."""
    
    def __init__(self):
        # Ensure required API keys are set
        _set_env("ANTHROPIC_API_KEY")
        
        # Initialize the language model
        self.llm = ChatAnthropic(
            model="claude-3-sonnet-20240229",
            temperature=0,
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        
        # Create the weather tool
        self.weather_tool = create_weather_tool()
        
        # Initialize the agent with tools
        self.agent = initialize_agent(
            tools=[self.weather_tool],
            llm=self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            handle_parsing_errors=True
        )
    
    def get_weather(self, query: str) -> str:
        """Get weather information based on a natural language query."""
        try:
            response = self.agent.run(query)
            return response
        except Exception as e:
            return f"Error: {str(e)}"
    
    def chat(self):
        """Start an interactive chat session with the weather agent."""
        print("🌤️  Weather Agent initialized!")
        print("Ask me about the weather in any city. Type 'quit' to exit.")
        print("Examples:")
        print("  - What's the weather in London?")
        print("  - Check the weather in Tokyo")
        print("  - How's the weather in New York City?")
        print("-" * 50)
        
        while True:
            try:
                user_input = input("\n🌍 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("👋 Goodbye!")
                    break
                
                if not user_input:
                    continue
                
                print("\n🤖 Agent: ", end="")
                response = self.get_weather(user_input)
                print(response)
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")


def main():
    """Main function to run the weather agent."""
    print("Setting up Weather Agent...")
    
    # Check if OpenWeather API key is set
    if not os.getenv("OPENWEATHER_API_KEY"):
        print("\n⚠️  OpenWeather API Key Setup Required:")
        print("1. Go to https://openweathermap.org/api")
        print("2. Sign up for a free account")
        print("3. Get your API key")
        print("4. Set it as an environment variable: export OPENWEATHER_API_KEY='your_key_here'")
        print("5. Or create a .env file with: OPENWEATHER_API_KEY=your_key_here")
        
        # Ask if they want to set it now
        set_now = input("\nWould you like to set the API key now? (y/n): ").lower()
        if set_now == 'y':
            _set_env("OPENWEATHER_API_KEY")
        else:
            print("You can still test the agent, but weather queries will show an error message.")
    
    # Create and start the agent
    agent = WeatherAgent()
    agent.chat()


if __name__ == "__main__":
    main()