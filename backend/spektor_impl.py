def correlate_embeddings(app, this_embedding, known_embeddings):

    import numpy as np

    samples = []

    for other in known_embeddings:
        mean = np.mean([this_embedding, other], axis=0)
        diff = np.abs(this_embedding - other)
        v = np.concatenate([[np.mean(diff), np.median(diff), np.std(diff), np.max(diff)], mean, diff])
        samples.append(v)

    X = np.array(samples)

    ridge_resp = app.config['ridge_reg'].predict(X)

    X = np.hstack((X, ridge_resp[:, np.newaxis]))

    y_hat = app.config['xgb_clf'].predict_proba(X)

    return y_hat[:, 1].astype(float)


def on_analyze(app, js, known_faces, NBEST=5):

    import numpy as np
    this_embedding = np.array(js['embedding'])
    NBEST = js['nbest']

    if len(known_faces) == 0:
        return []

    import json
    known_embeddings = [json.loads(face.embedding) for face in known_faces]

    scores = correlate_embeddings(app, this_embedding, np.array(known_embeddings))

    known_personas = [f.avatars[0].persona_id for f in known_faces]

    matched_ranked = sorted(zip(scores, known_personas), reverse=True)[:NBEST]

    return matched_ranked
