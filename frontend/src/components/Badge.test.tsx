import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Badge } from "./Badge";

describe("Badge", () => {
  it("renders its label text", () => {
    render(<Badge variant="success">Indexed</Badge>);
    expect(screen.getByText("Indexed")).toBeInTheDocument();
  });

  it("applies the variant's accent color class", () => {
    render(<Badge variant="danger">Failed</Badge>);
    expect(screen.getByText("Failed")).toHaveClass("text-danger");
  });
});
