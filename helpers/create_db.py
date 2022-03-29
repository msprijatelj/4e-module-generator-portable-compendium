def create_db(fn, splt):
    print(f"Filename: {fn}")
    with open(f'sources/{fn}', 'r+', encoding='utf-8-sig') as f:
        contents = f.read()

    db_schema = get_schema(contents)
    db_values = get_values(contents, splt)

    db = [{}]*len(db_values)
    for i, vals in enumerate(db_values):
        db[i] = dict(zip(db_schema.copy(), vals))

    return db

def get_schema(contents):
    insert_index = contents.find("INSERT")
    query = contents[:insert_index].strip()
    lines = query.split("\n")
    schema = []
    for line in lines:
        line = line.strip()
        start_index = line.find("`")
        if start_index == 0:
            end_index = line.find("`", start_index + 1)
            col_name = line[start_index + 1:end_index]
            schema.append(col_name)
    return schema

def get_values(contents, splt):
    insert_index = contents.find("INSERT")

    # Retrieve only the INSERT queries
    query = contents[insert_index:].strip()
    queries = query.split("\n")

    values = [tuple()]*len(queries)
    for i, q in enumerate(queries):
        # Take off the INSERT part of the query
        value_str = q.split("VALUES ('")[1]
        # Take off the tail of the query
        value_str = "".join(value_str.split("');")[:-1])
        values[i] = tuple(value_str.split(splt))
    return values

if __name__ == "__main__":
    DATABASE = create_db("ddiMonster.sql", "','")
    print(DATABASE[0])