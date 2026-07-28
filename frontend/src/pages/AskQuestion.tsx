import { useMutation } from "@tanstack/react-query";
import { Loader2, Send } from "lucide-react";
import { useState, type SubmitEvent } from "react";
import Markdown from "react-markdown";
import { askQuestion } from "../api/query";
import { Button } from "../components/Button";
import { Card } from "../components/Card";
import type { QueryResponse } from "../types";

interface Turn {
  id: string;
  question: string;
  response?: QueryResponse;
}

export function AskQuestion() {
  const [turns, setTurns] = useState<Turn[]>([]);
  const [question, setQuestion] = useState("");

  const ask = useMutation({
    mutationFn: askQuestion,
    onSuccess: (response, question) => {
      setTurns((prev) => [...prev, { id: crypto.randomUUID(), question, response }]);
    },
  });

  function handleSubmit(event: SubmitEvent) {
    event.preventDefault();
    if (!question.trim()) return;
    ask.mutate(question);
    setQuestion("");
  }

  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-4">
      <h1 className="text-xl font-semibold">Ask a Question</h1>
      <p className="text-sm text-on-surface-muted">
        Answers are generated only from documents belonging to your organization.
      </p>

      <div className="flex flex-col gap-4">
        {turns.map((turn) => (
          <div key={turn.id} className="flex flex-col gap-2">
            <Card className="ml-auto bg-surface-container-high">{turn.question}</Card>
            {turn.response && (
              <Card>
                <div className="prose prose-sm max-w-none prose-p:my-2 prose-headings:my-2">
                  <Markdown>{turn.response.answer}</Markdown>
                </div>
                {turn.response.sources.length > 0 && (
                  <div className="mt-3 flex flex-wrap gap-2 border-t border-surface-border pt-2">
                    {turn.response.sources.map((s) => (
                      <span
                        key={`${s.documentId}-${s.chunkIndex}`}
                        className="rounded border border-surface-border px-2 py-0.5 font-mono text-xs text-on-surface-muted"
                      >
                        {s.filename}
                      </span>
                    ))}
                  </div>
                )}
              </Card>
            )}
          </div>
        ))}
        {ask.isPending && (
          <Card className="flex items-center gap-2 text-on-surface-muted">
            <Loader2 size={16} className="animate-spin" />
            Thinking...
          </Card>
        )}
      </div>

      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask anything about your documents..."
          className="flex-1 rounded-md border border-surface-border bg-surface-container px-3 py-2 text-sm focus:border-accent focus:outline-none"
        />
        <Button type="submit" disabled={ask.isPending}>
          <Send size={16} />
          Send
        </Button>
      </form>
    </div>
  );
}
