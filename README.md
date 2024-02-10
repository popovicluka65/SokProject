### Members
- SV4/2021 Luka Popovic
- SV5/2021 Matija Popovic
- SV43/2021 Miroslav Blagojevic
- SV51/2021 Sava Janjic
## Project Structure

### Project Components
- **Core**: Main functionality with Graph
- **Plugins**:
  - **Data Source**: Parses specified documents and creates a graph.
  - **Visualizer**: Creates HTML with graph structure and adds functions such as zoom, pan, drag and drop, and mouseover.
- **API**: Abstractions for Data Source and Visualizer plugins

### API
- **Plugin Abstraction**: `GraphParserBase` class implemented by parser plugins.
- **Visualizer Abstraction**: `GraphVisualiserBase` class implemented by visualizer plugins.
- **Model Graph**: Represents the structure of a graph. It includes nodes holding info such as id and additional values, and edges      representing connections between nodes.

### Data Source Plugins
- RDF: Cyclic graph structure. Valid TTL document creates a graph. Date parsing requires date format like (%Y-%m-%dT%H:%M:%S.%fZ).
- JSON: Acyclic graph structure. Configured via `config.json`. Attribute for creating back edge for Graph present in the JSON file        determines graph type. Date format for parsing: (%Y-%m-%dT%H:%M:%S.%fZ).

### Visualizer Plugins
- **Simple Visualizer**: Displays only the ID of the node.
- **Block Visualizer**: Displays all attributes of the node.

### Database, Search, and Filters
- **Database**: Neo4J utilized.
- **Search**: Searches all nodes and edges containing any value in node values.
- **Filter**: Compares node values with the forwarded value. Date format for comparison: (%Y-%m-%dT%H:%M:%S.%fZ).

### Workspaces
- Workspace displays a certain graph. Users can create new workspaces with a button.

## Installation

1. **Clone the Repository**:
    ```
    git clone git@github.com:popovicluka65/SokProject.git
    ```
2. **Create Virtual Environment**:
    ```
    python -m venv venvSok
    ```
3. **Activate Virtual Environment**:
    ```
    venvSok\Scripts\activate
    ```
4. **Install Dependencies**:
    ```
    pip install -r requirements.txt
    ```
5. **Start Neo4j Database**:
-Open Neo4j application, create a database, and start it.

6. **Install Project Components**:
- For installing all components:
  ```
  .\install.bat
  ```
- For installing specific components:
  ```
  pip install .\Core\
  pip install .\API\
  pip install .\GraphParserJSON\
  pip install .\GraphParserRDF\
  pip install .\GraphVisualiserSimple\
  pip install .\GraphVisualiserBlock\
  ```
7. **Navigate to Project Directory**:
   ```
   cd .\graph_explorer\
   ```
8. **Run Server**:
   ```
   python manage.py runserver
   ```
9. **Open in Browser**:
Open the following link in your browser: http://127.0.0.1:8000/