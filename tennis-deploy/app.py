from shiny import App, ui, render, reactive
import requests
import math

# Tennis API Configuration
API_URL = "http://3.139.106.131:8000"

# ATP Top 30 Players with Countries
players = {
    "Djokovic N.": {"rank": 1, "country": "Serbia"},
    "Alcaraz C.": {"rank": 2, "country": "Spain"},
    "Medvedev D.": {"rank": 3, "country": "Russia"},
    "Sinner J.": {"rank": 4, "country": "Italy"},
    "Rublev A.": {"rank": 5, "country": "Russia"},
    "Tsitsipas S.": {"rank": 6, "country": "Greece"},
    "Rune H.": {"rank": 7, "country": "Denmark"},
    "Hurkacz H.": {"rank": 8, "country": "Poland"},
    "Fritz T.": {"rank": 9, "country": "USA"},
    "Ruud C.": {"rank": 10, "country": "Norway"},
    "Paul T.": {"rank": 11, "country": "USA"},
    "Dimitrov G.": {"rank": 12, "country": "Bulgaria"},
    "Khachanov K.": {"rank": 13, "country": "Russia"},
    "Shapovalov D.": {"rank": 14, "country": "Canada"},
    "Berrettini M.": {"rank": 15, "country": "Italy"},
    "Norrie C.": {"rank": 16, "country": "Great Britain"},
    "Musetti L.": {"rank": 17, "country": "Italy"},
    "Tiafoe F.": {"rank": 18, "country": "USA"},
    "De Minaur A.": {"rank": 19, "country": "Australia"},
    "Shelton B.": {"rank": 20, "country": "USA"},
    "Zverev A.": {"rank": 21, "country": "Germany"},
    "Auger-Aliassime F.": {"rank": 22, "country": "Canada"},
    "Korda S.": {"rank": 23, "country": "USA"},
    "Cerundolo F.": {"rank": 24, "country": "Argentina"},
    "Jarry N.": {"rank": 25, "country": "Chile"},
    "Bublik A.": {"rank": 26, "country": "Kazakhstan"},
    "Mannarino A.": {"rank": 27, "country": "France"},
    "Machac T.": {"rank": 28, "country": "Czech Republic"},
    "Nakashima B.": {"rank": 29, "country": "USA"},
    "Draper J.": {"rank": 30, "country": "Great Britain"}
}

def get_prediction(rank1, rank2, surface):
    """Call the tennis prediction API with fallback logic"""
    try:
        response = requests.get(f"{API_URL}/predict", params={
            "player1_rank": rank1,
            "player2_rank": rank2,
            "surface": surface
        }, timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            result["source"] = "ML API"
            return result
        else:
            return create_fallback_prediction(rank1, rank2)
    except:
        return create_fallback_prediction(rank1, rank2)

def create_fallback_prediction(rank1, rank2):
    """Generate predictions when API is unavailable"""
    rank_diff = rank2 - rank1
    prob1 = 1 / (1 + math.exp(-rank_diff * 0.02))
    prob1 = max(0.1, min(0.9, prob1))
    
    return {
        "player1_win_prob": prob1,
        "player2_win_prob": 1 - prob1,
        "favorite": "Player 1" if prob1 > 0.5 else "Player 2",
        "source": "Fallback"
    }

def check_api_connection():
    """Verify API connectivity"""
    try:
        response = requests.get(f"{API_URL}/", timeout=3)
        return response.status_code == 200
    except:
        return False

# Application UI
app_ui = ui.page_fluid(
    ui.tags.head(
        ui.tags.style("""
            .header { 
                background: linear-gradient(135deg, #2E8B57, #228B22);
                color: white; padding: 2rem; margin-bottom: 1rem;
                border-radius: 10px; text-align: center;
            }
            .result-card { 
                border: 2px solid #ddd; border-radius: 10px; 
                padding: 1.5rem; margin: 0.5rem; text-align: center;
                background: white; box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .winner { border-color: #28a745; background: #f8fff9; }
            .loser { border-color: #dc3545; background: #fff8f8; }
            .sidebar { 
                background: #f8f9fa; padding: 1rem; border-radius: 10px; 
                font-size: 0.9em;
            }
            .sidebar h3 { 
                font-size: 1.1em; margin-bottom: 0.8rem; 
            }
            .sidebar label { 
                font-size: 0.85em; font-weight: 600; 
            }
            .sidebar .form-select { 
                font-size: 0.8em; padding: 0.4rem; 
            }
            .chart-bar { 
                padding: 0.5rem; color: white; margin: 0.2rem 0; 
                border-radius: 4px; transition: all 0.3s ease;
            }
        """)
    ),
    
    ui.div(
        ui.h1("🎾 ATP Tennis Match Predictor"),
        ui.p("Professional tennis match outcome predictions powered by machine learning"),
        class_="header"
    ),
    
    ui.page_sidebar(
        ui.sidebar(
            ui.div(
                ui.h3("Match Setup"),
                
                ui.p("Player 1:", style="margin-bottom: 0.3rem; font-weight: bold; font-size: 0.9em;"),
                ui.input_select("player1", None,
                              choices={str(data['rank']): f"{name} (#{data['rank']})" 
                                     for name, data in players.items()}),
                
                ui.p("Player 2:", style="margin-bottom: 0.3rem; font-weight: bold; font-size: 0.9em;"),
                ui.input_select("player2", None,
                              choices={str(data['rank']): f"{name} (#{data['rank']})" 
                                     for name, data in players.items()},
                              selected="10"),
                
                ui.p("Surface:", style="margin-bottom: 0.3rem; font-weight: bold; font-size: 0.9em;"),
                ui.input_select("surface", None,
                              choices={"Hard": "Hard", "Clay": "Clay", "Grass": "Grass"}),
                
                ui.br(),
                
                ui.input_action_button("predict", "Predict", 
                                     class_="btn-success w-100"),
                
                ui.br(), ui.br(),
                
                ui.output_ui("connection_status"),
                
                class_="sidebar"
            )
        ),
        
        ui.output_ui("prediction_results")
    )
)

def server(input, output, session):
    
    @output
    @render.ui
    def connection_status():
        if check_api_connection():
            return ui.div(
                ui.p("🟢 API: Connected", style="color: green; margin: 0; font-weight: bold; font-size: 0.8em;"),
                ui.p("ML Model Active", style="color: #666; font-size: 0.7em; margin: 0;")
            )
        else:
            return ui.div(
                ui.p("🔴 API: Offline", style="color: red; margin: 0; font-weight: bold; font-size: 0.8em;"),
                ui.p("Fallback Mode", style="color: #666; font-size: 0.7em; margin: 0;")
            )
    
    @output
    @render.ui
    @reactive.event(input.predict)
    def prediction_results():
        # Extract player information
        p1_rank = int(input.player1())
        p2_rank = int(input.player2())
        p1_name = [name for name, data in players.items() if data['rank'] == p1_rank][0]
        p2_name = [name for name, data in players.items() if data['rank'] == p2_rank][0]
        p1_country = players[p1_name]['country']
        p2_country = players[p2_name]['country']
        
        # Generate prediction
        result = get_prediction(p1_rank, p2_rank, input.surface())
        
        # Determine formatting based on prediction
        p1_is_favorite = result['player1_win_prob'] > 0.5
        confidence_level = abs(result['player1_win_prob'] - 0.5) * 200
        
        return ui.div(
            ui.h2("Match Prediction Analysis"),
            
            # Player win probability cards
            ui.row(
                ui.column(6,
                    ui.div(
                        ui.h3(f"🏆 {p1_name}"),
                        ui.h1(f"{result['player1_win_prob']:.1%}", 
                               style="font-weight: bold; color: #28a745;" if p1_is_favorite else "font-weight: bold; color: #dc3545;"),
                        ui.p(f"ATP Ranking #{p1_rank}"),
                        ui.p(f"Country: {p1_country}"),
                        class_="result-card " + ("winner" if p1_is_favorite else "loser")
                    )
                ),
                ui.column(6,
                    ui.div(
                        ui.h3(f"🏆 {p2_name}"),
                        ui.h1(f"{result['player2_win_prob']:.1%}",
                               style="font-weight: bold; color: #28a745;" if not p1_is_favorite else "font-weight: bold; color: #dc3545;"),
                        ui.p(f"ATP Ranking #{p2_rank}"),
                        ui.p(f"Country: {p2_country}"),
                        class_="result-card " + ("winner" if not p1_is_favorite else "loser")
                    )
                )
            ),
            
            # Match analysis details
            ui.div(
                ui.h4("Match Analysis"),
                ui.row(
                    ui.column(3, 
                        ui.div(
                            ui.strong("Predicted Winner:"), ui.br(), 
                            ui.span(result['favorite'], style="color: #28a745; font-weight: bold;")
                        )
                    ),
                    ui.column(3, 
                        ui.div(
                            ui.strong("Court Surface:"), ui.br(), 
                            ui.span(input.surface())
                        )
                    ),
                    ui.column(3, 
                        ui.div(
                            ui.strong("Ranking Difference:"), ui.br(), 
                            ui.span(f"{abs(p1_rank - p2_rank)} positions")
                        )
                    ),
                    ui.column(3, 
                        ui.div(
                            ui.strong("Confidence Level:"), ui.br(), 
                            ui.span(f"{confidence_level:.0f}%", 
                                   style="color: #28a745;" if confidence_level > 30 else "color: #ffc107;")
                        )
                    )
                ),
                style="background: #f8f9fa; padding: 1.5rem; border-radius: 8px; margin-top: 1rem;"
            ),
            
            # Visual probability comparison
            ui.div(
                ui.h4("Win Probability Visualization"),
                ui.div(
                    ui.div(
                        f"{p1_name}: {result['player1_win_prob']:.1%}",
                        class_="chart-bar",
                        style=f"background: linear-gradient(90deg, #28a745, #20c997); "
                              f"width: {result['player1_win_prob']*100}%;"
                    ),
                    ui.div(
                        f"{p2_name}: {result['player2_win_prob']:.1%}",
                        class_="chart-bar", 
                        style=f"background: linear-gradient(90deg, #dc3545, #fd7e14); "
                              f"width: {result['player2_win_prob']*100}%;"
                    )
                ),
                style="background: white; padding: 1.5rem; border-radius: 8px; margin-top: 1rem; border: 1px solid #ddd;"
            ),
            
            # Prediction source information
            ui.div(
                ui.p(f"Prediction generated using: {result.get('source', 'Unknown')} Model", 
                     style="text-align: center; margin: 1rem 0; color: #666; font-style: italic;")
            )
        )

app = App(app_ui, server)