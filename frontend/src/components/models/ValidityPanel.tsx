import React from "react";
import { Card, CardHeader, CardTitle, CardContent } from "../ui/Card";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "../ui/Accordion";
import { FileText, AlertTriangle, CheckCircle2, Info } from "lucide-react";
import type { ModelValidity } from "../../types";

interface ValidityPanelProps {
  validity: ModelValidity;
}

export function ValidityPanel({ validity }: ValidityPanelProps): React.ReactElement {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Info className="h-5 w-5 text-primary" />
          Scientific Validity & Limitations
        </CardTitle>
      </CardHeader>
      <CardContent>
        <Accordion type="single" collapsible defaultValue="sources">
          {/* Sources */}
          <AccordionItem value="sources">
            <AccordionTrigger className="text-sm font-medium">
              <div className="flex items-center gap-2">
                <FileText className="h-4 w-4" />
                Sources & References
              </div>
            </AccordionTrigger>
            <AccordionContent>
              <ul className="space-y-2">
                {validity.sources.map((source, idx) => (
                  <li
                    key={idx}
                    className="flex items-start gap-2 text-sm text-gray-600 dark:text-gray-400"
                  >
                    <CheckCircle2 className="h-4 w-4 text-emerald-500 mt-0.5 shrink-0" />
                    <code className="text-xs bg-gray-100 dark:bg-gray-800 px-2 py-0.5 rounded">
                      {source}
                    </code>
                  </li>
                ))}
              </ul>
            </AccordionContent>
          </AccordionItem>

          {/* Notes */}
          <AccordionItem value="notes">
            <AccordionTrigger className="text-sm font-medium">
              <div className="flex items-center gap-2">
                <AlertTriangle className="h-4 w-4" />
                Notes & Limitations
              </div>
            </AccordionTrigger>
            <AccordionContent>
              <div className="prose prose-sm dark:prose-invert max-w-none">
                {validity.notesMd.split("\n").map((line, idx) => {
                  const trimmed = line.trim();
                  if (!trimmed) return null;
                  if (trimmed.startsWith("-")) {
                    const content = trimmed.substring(1).trim();
                    return (
                      <div key={idx} className="flex items-start gap-2 mb-2 text-sm">
                        <span className="text-primary">•</span>
                        <span
                          className="text-gray-600 dark:text-gray-400"
                          dangerouslySetInnerHTML={{
                            __html: content
                              .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
                              .replace(/`(.*?)`/g, "<code class='text-xs bg-gray-100 dark:bg-gray-800 px-1 py-0.5 rounded'>$1</code>"),
                          }}
                        />
                      </div>
                    );
                  }
                  return (
                    <p
                      key={idx}
                      className="text-sm text-gray-600 dark:text-gray-400 mb-2"
                      dangerouslySetInnerHTML={{
                        __html: trimmed
                          .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
                          .replace(/`(.*?)`/g, "<code class='text-xs bg-gray-100 dark:bg-gray-800 px-1 py-0.5 rounded'>$1</code>"),
                      }}
                    />
                  );
                })}
              </div>
            </AccordionContent>
          </AccordionItem>

          {/* Metrics */}
          <AccordionItem value="metrics">
            <AccordionTrigger className="text-sm font-medium">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4" />
                Available Metrics
              </div>
            </AccordionTrigger>
            <AccordionContent>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left py-2 px-3 font-medium text-gray-700 dark:text-gray-300">
                        Metric
                      </th>
                      <th className="text-left py-2 px-3 font-medium text-gray-700 dark:text-gray-300">
                        Value
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {validity.metrics.map((metric, idx) => (
                      <tr
                        key={idx}
                        className="border-b border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800/50"
                      >
                        <td className="py-2 px-3 text-gray-600 dark:text-gray-400">
                          {metric.key}
                        </td>
                        <td className="py-2 px-3">
                          <code className="text-xs font-mono bg-gray-100 dark:bg-gray-800 px-2 py-0.5 rounded">
                            {metric.value}
                          </code>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      </CardContent>
    </Card>
  );
}
