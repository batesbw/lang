#!/usr/bin/env python3
"""
Script to visualize the LangGraph workflow and save it as an image.
This works on Linux and generates a visual representation of the workflow.
"""

import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.main_orchestrator import create_workflow


def visualize_workflow():
    """Generate and save a visual representation of the workflow."""
    print("🎨 Generating LangGraph Workflow Visualization")
    print("=" * 50)
    
    try:
        # Create the workflow
        print("📊 Creating workflow graph...")
        workflow = create_workflow()
        
        # Compile the workflow
        print("⚙️  Compiling workflow...")
        app = workflow.compile()
        
        # Get the graph
        graph = app.get_graph()
        
        # Try to create a visual representation
        try:
            # Method 1: Try to use the built-in draw method
            print("🖼️  Attempting to generate PNG visualization...")
            
            # This will create a PNG file if graphviz is available
            png_data = graph.draw_png()
            
            # Save to file
            output_file = "workflow_visualization.png"
            with open(output_file, "wb") as f:
                f.write(png_data)
            
            print(f"✅ Visualization saved as: {output_file}")
            print(f"   You can open it with: xdg-open {output_file}")
            return True
            
        except Exception as png_error:
            print(f"⚠️  PNG generation failed: {png_error}")
            
            # Method 2: Try to generate SVG
            try:
                print("🖼️  Attempting to generate SVG visualization...")
                svg_data = graph.draw_svg()
                
                output_file = "workflow_visualization.svg"
                with open(output_file, "w") as f:
                    f.write(svg_data)
                
                print(f"✅ SVG visualization saved as: {output_file}")
                print(f"   You can open it with: xdg-open {output_file}")
                return True
                
            except Exception as svg_error:
                print(f"⚠️  SVG generation failed: {svg_error}")
                
                # Method 3: Generate text-based representation
                print("📝 Generating text-based visualization...")
                generate_text_visualization(graph)
                return True
                
    except Exception as e:
        print(f"❌ Workflow visualization failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def generate_text_visualization(graph):
    """Generate a text-based visualization of the workflow."""
    print("\n" + "=" * 60)
    print("📋 WORKFLOW STRUCTURE (Text Representation)")
    print("=" * 60)
    
    # Get nodes and edges
    nodes = list(graph.nodes.keys())
    edges = graph.edges
    
    print("\n🔗 NODES:")
    print("-" * 20)
    for i, node in enumerate(nodes, 1):
        if node.startswith("__"):
            print(f"  {i}. {node} (System Node)")
        else:
            print(f"  {i}. {node}")
    
    print("\n➡️  EDGES (Workflow Flow):")
    print("-" * 30)
    for i, edge in enumerate(edges, 1):
        source = edge.source
        target = edge.target
        conditional = " (Conditional)" if edge.conditional else ""
        print(f"  {i}. {source} → {target}{conditional}")
    
    print("\n🔄 WORKFLOW SEQUENCE:")
    print("-" * 25)
    print("  1. START")
    print("  2. authentication")
    print("     ├─ Success → prepare_flow_request")
    print("     └─ Failure → END")
    print("  3. prepare_flow_request")
    print("     └─ → flow_builder")
    print("  4. flow_builder")
    print("     ├─ Success → prepare_deployment_request")
    print("     └─ Failure → END")
    print("  5. prepare_deployment_request")
    print("     └─ → deployment")
    print("  6. deployment")
    print("     └─ → END")
    
    print("\n💡 AGENT RESPONSIBILITIES:")
    print("-" * 30)
    print("  🔐 authentication: Salesforce OAuth/JWT authentication")
    print("  📝 prepare_flow_request: Create FlowBuildRequest with default values")
    print("  🏗️  flow_builder: Generate Flow XML using BasicFlowXmlGeneratorTool")
    print("  📦 prepare_deployment_request: Create DeploymentRequest with session")
    print("  🚀 deployment: Deploy Flow to Salesforce using SalesforceDeployerTool")
    
    # Save text visualization to file
    output_file = "workflow_structure.txt"
    with open(output_file, "w") as f:
        f.write("SALESFORCE AGENT WORKFORCE - WORKFLOW STRUCTURE\n")
        f.write("=" * 60 + "\n\n")
        
        f.write("NODES:\n")
        for i, node in enumerate(nodes, 1):
            status = " (System Node)" if node.startswith("__") else ""
            f.write(f"  {i}. {node}{status}\n")
        
        f.write("\nEDGES:\n")
        for i, edge in enumerate(edges, 1):
            conditional = " (Conditional)" if edge.conditional else ""
            f.write(f"  {i}. {edge.source} → {edge.target}{conditional}\n")
        
        f.write("\nWORKFLOW SEQUENCE:\n")
        f.write("  START → authentication → prepare_flow_request → flow_builder → prepare_deployment_request → deployment → END\n")
    
    print(f"\n📄 Text visualization also saved as: {output_file}")
    print("=" * 60)


def install_graphviz_instructions():
    """Provide instructions for installing graphviz for better visualizations."""
    print("\n💡 FOR BETTER VISUALIZATIONS:")
    print("-" * 35)
    print("To generate PNG/SVG visualizations, install graphviz:")
    print("  sudo apt-get update")
    print("  sudo apt-get install graphviz")
    print("  pip install graphviz")
    print("\nThen run this script again for image-based visualizations!")


def main():
    """Main function to run the visualization."""
    print("🚀 LangGraph Workflow Visualizer")
    print("=" * 35)
    
    success = visualize_workflow()
    
    if success:
        print("\n🎉 Visualization completed successfully!")
        install_graphviz_instructions()
    else:
        print("\n❌ Visualization failed. Check the error messages above.")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 