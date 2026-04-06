# Auto Mode Design

Add `--auto` flag to `analyze` command for quick analysis with preset defaults.

## Usage

```bash
python -m cli.main analyze --auto AAPL
python -m cli.main analyze -a TSLA
```

## Default Configuration

| Setting | Value |
|---------|-------|
| Output Language | Chinese |
| Analysts | All (market, social, news, fundamentals) |
| Research Depth | Deep (5 rounds) |
| LLM Provider | Anthropic |
| Quick-Thinking LLM | Claude Sonnet 4.5 (`claude-4-5-sonnet-20250929`) |
| Deep-Thinking LLM | Claude Opus 4.5 (`claude-opus-4-5-20251101`) |
| Effort Level | High |
| Analysis Date | Today (auto-generated) |

## Implementation

### 1. Modify `analyze` command signature

File: `cli/main.py`

```python
@app.command()
def analyze(
    auto: Optional[str] = typer.Option(
        None,
        "--auto",
        "-a",
        help="Auto mode: skip prompts, use defaults. Value is the ticker symbol."
    )
):
    if auto:
        run_analysis_auto(auto)
    else:
        run_analysis()
```

### 2. Add `run_analysis_auto()` function

File: `cli/main.py`

```python
def run_analysis_auto(ticker: str):
    """Run analysis with preset defaults, only ticker required."""
    import datetime
    
    selections = {
        "ticker": ticker.strip().upper(),
        "analysis_date": datetime.datetime.now().strftime("%Y-%m-%d"),
        "analysts": [AnalystType.MARKET, AnalystType.SOCIAL, AnalystType.NEWS, AnalystType.FUNDAMENTALS],
        "research_depth": 5,
        "llm_provider": "anthropic",
        "backend_url": os.getenv("ANTHROPIC_API_URL", os.getenv("ANTHROPIC_BASE_URL", "https://api.anthropic.com/")),
        "shallow_thinker": "claude-4-5-sonnet-20250929",
        "deep_thinker": "claude-opus-4-5-20251101",
        "google_thinking_level": None,
        "openai_reasoning_effort": None,
        "anthropic_effort": "high",
        "output_language": "Chinese",
    }
    
    console.print(Panel(
        f"[bold]Auto Mode[/bold]\n"
        f"Ticker: {selections['ticker']}\n"
        f"Date: {selections['analysis_date']}\n"
        f"Language: Chinese | Analysts: All | Depth: Deep\n"
        f"LLM: Anthropic (Sonnet 4.5 / Opus 4.5) | Effort: High",
        border_style="green"
    ))
    
    _run_analysis_with_selections(selections)
```

### 3. Extract shared logic

Refactor `run_analysis()` to extract core logic:

```python
def run_analysis():
    """Interactive mode - prompt for all selections."""
    selections = get_user_selections()
    _run_analysis_with_selections(selections)


def _run_analysis_with_selections(selections: dict):
    """Core analysis logic, shared by interactive and auto modes."""
    # Move existing run_analysis() logic here (lines 933-end)
    # - Config construction
    # - Graph initialization  
    # - Display loop
    # - Report saving
```

## Files Changed

1. `cli/main.py`
   - Modify `analyze()` command to accept `--auto` option
   - Add `run_analysis_auto()` function
   - Extract `_run_analysis_with_selections()` from `run_analysis()`

## Testing

```bash
# Auto mode
python -m cli.main analyze --auto AAPL

# Interactive mode (unchanged)
python -m cli.main analyze
```
