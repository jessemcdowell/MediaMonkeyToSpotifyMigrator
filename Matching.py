
def disable_log():
    global log, format_candidate
    log = lambda text: 0
    format_candidate = lambda candidate: 'candidate'

disable_log()

def enable_log(candidate_formatter):
    global log, format_candidate
    log = lambda text: print(f'  # Matching: {text}')
    format_candidate = candidate_formatter

def best_match(candidates, matchers, minimum_score):
    best_candidate = None
    best_candidate_score = -1

    for candidate in candidates:
        score = sum(matcher(candidate) for matcher in matchers)
        log(f'- candidate: {format_candidate(candidate)}, score: {score}')
        if score > best_candidate_score and score >= minimum_score:
            best_candidate = candidate
            best_candidate_score = score

    log(f'winner: {format_candidate(best_candidate) if best_candidate else "None"}')
    return best_candidate

def boolean_matcher(predicate, score):
    return lambda input: score if predicate(input) else 0

def _strings_are_equal(source, compare_to, total_possible_score):
    if source == compare_to:
        return total_possible_score
    if source.lower() == compare_to.lower():
        return total_possible_score - 1
    return 0

def text_matcher(selector, source, total_possible_score):
    def break_into_chunks(source):
        chunk_size = 4
        if len(source) <= chunk_size:
            yield source
            return
        index = 0;
        while (index + chunk_size) <= len(source):
            yield source[index:index + chunk_size]
            index += 1

    def match(source, compare_to, total_possible_score):
        score = _strings_are_equal(source, compare_to, total_possible_score)
        if score > 0:
            return score

        score = 0
        sequential_match_index = 0
        number_of_chunks = 0
        for chunk in break_into_chunks(source):
            found_at_index = compare_to.find(chunk)
            if found_at_index >= 0:
                if found_at_index == sequential_match_index:
                    score += 1
                elif found_at_index < sequential_match_index:
                    score += 0.8
                else:
                    score += 0.7
                sequential_match_index = found_at_index + 1
            else:
                sequential_match_index = -1
            number_of_chunks += 1

        return score * total_possible_score / number_of_chunks

    def evaluate_function(input):
        compare_source = source
        compare_input = selector(input)
        return match(compare_source, compare_input, total_possible_score * 0.06) + \
               match(compare_input, compare_source, total_possible_score * 0.04) + \
               match(compare_source.lower(), compare_input.lower(), total_possible_score * 0.5) + \
               match(compare_input.lower(), compare_source.lower(), total_possible_score * 0.4);

    return evaluate_function

def simple_text_matcher(selector, source, total_possible_score):
    def match(source, compare_to, total_possible_score):
        equal_score = _strings_are_equal(source, compare_to, total_possible_score)
        if equal_score > 0:
            return equal_score

        found_at_index = compare_to.lower().find(source.lower())
        if found_at_index >= 0:
            factor = 1
            if found_at_index == len(compare_to) - len(source):
                factor = 0.7
            elif found_at_index > 0:
                factor = 0.3
            return total_possible_score * (len(source) / len(compare_to)) * factor

        return 0

    return lambda input: match(source, selector(input), total_possible_score)
