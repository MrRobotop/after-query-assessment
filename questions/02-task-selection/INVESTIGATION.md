# Task selection investigation

The question supplies six issue descriptions for a hypothetical 60,000-line payments service. The service, incident logs, schema, and tests were unavailable, so the comparison uses the tickets as written. The replay below is a fixture design with illustrative values and no measured service output.

## Compare the six tickets

| Candidate | What the ticket already gives away | What an investigator would still have to establish |
| --- | --- | --- |
| (1) Blank usernames | Endpoint, invalid input and required rejection | Where the request schema enforces the rule and how the API reports validation errors |
| (2) Merchant balance | Visible symptom, concurrent trigger and suspected components | Which state first diverges and whether the divergence comes from a lost write, a stale read or reconciliation |
| (3) Environment variable rename | Old name, new name and intended scope | Every consumer and deployment reference, plus any compatibility obligation actually present in the repository |
| (4) CI connection failures | Failure signature, rough frequency and environment | A failing runner timeline and a way to recreate equivalent startup or networking conditions on demand |
| (5) CLI JSON flag | Entry point and output mode | The callers, established output conventions and contract for structured output |
| (6) Webhook context | Destination type and the eight packages it should span | The call sites and existing interfaces, including any real semantic differences between handlers |

(2) has both diagnostic depth and a prospective grading signal. The expected balance comes from committed ledger activity. The replay can vary the order of concurrent operations while holding their IDs and deltas fixed. (4) could also become a long-horizon task once the runner evidence supports stable replay. The symptoms alone leave that setup uncertain.

## Derive a controlled balance

Assume the real service's contract permits this fixture. Start one merchant at 10,000 cents and send two independent checkout operations with distinct IDs. Let the operations have signed ledger deltas of +300 and +500 cents. The expected balance for a read that should include both commits is `10,000 + 300 + 500 = 10,800` cents. A reconciliation cutoff that includes only the first commit has an expected snapshot balance of 10,300 cents. Whether the job is allowed to publish that earlier result after the second commit depends on its documented contract.

The investigator should first establish the service's opening-balance convention, which ledger entries count, and what each read and job promises to include. Use the two operation IDs to check that each successful checkout contributes exactly once. If either operation is rejected or rolled back, use the documented outcome and its committed entries when deriving the expected balance.

| Replay | Coordinate these events | Compare these observations |
| --- | --- | --- |
| Checkout commits | Start both checkout requests on distinct connections and order their commit attempts through the test setup. | Operation outcomes, committed entries by operation ID, and the derived and persisted balances after both transactions finish. |
| Cache refill | Hold a cache miss that has read the intermediate committed balance, finish the second checkout, then release the refill before starting a fresh merchant read. | The intermediate snapshot, Redis after the refill, and the fresh response and committed balance at the applicable visibility boundary. |
| Reconciliation | Pin a cutoff including the first commit, let the second checkout commit, then allow the job to publish and rerun at the same cutoff. | The cutoff-specific result, any persisted or cached balance after publication, and whether a replay writes or counts the same activity again. |

Use repository-supported coordination around the relevant boundaries and bounded waits. A checkout test that forces both writers to pass a point protected by a database lock could deadlock a correct implementation. For grading, retain the clean single-checkout case and compare clearly observable outcomes from the overlap, such as both successful checkout IDs appearing once and the merchant balance reflecting both at the documented read boundary.

For example, both ledger entries present with a persisted balance of 10,500 cents points toward how the persisted balance was derived or overwritten. A persisted balance of 10,800 with a cached and served balance of 10,300 after both commits points toward the read path or a cache publisher. A discrepancy that appears only after the job publishes moves investigation to what that job read and wrote. Each pattern narrows the next trace without establishing a root cause on its own.
