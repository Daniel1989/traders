from prompt import get_action, generate_prompt

if __name__ == '__main__':
    data = [
        {
            "date": "2024-04-10",
            "open": 7223,
            "high": 7271,
            "low": 7135,
            "close": 7204,
            "volume": 1999764
        },
        {
            "date": "2024-04-11",
            "open": 7177,
            "high": 7261,
            "low": 7088,
            "close": 7164,
            "volume": 2207334
        },
        {
            "date": "2024-04-12",
            "open": 7192,
            "high": 7479,
            "low": 7146,
            "close": 7472,
            "volume": 1980210
        },
        {
            "date": "2024-04-15",
            "open": 7497,
            "high": 7790,
            "low": 7303,
            "close": 7436,
            "volume": 4756248
        },
        {
            "date": "2024-04-16",
            "open": 7490,
            "high": 7508,
            "low": 7320,
            "close": 7368,
            "volume": 2717032
        }
    ]
    history = ''
    for item in data:
        history += f"date: {item['date']}, open: {item['open']}, high: {item['high']}, low: {item['low']}, close: {item['close']}, volume: {item['volume']}\n"
    curr_input = ["2024-04-17", 7361, "gold create new history high price",
                  "bullish", "short-term profits", "high", "silver", history]
    prompt_lib_file = "prompt_template/ask_action.txt"
    prompt = generate_prompt(curr_input, prompt_lib_file)
    print(prompt)
    res = get_action(prompt)
    print(res)
