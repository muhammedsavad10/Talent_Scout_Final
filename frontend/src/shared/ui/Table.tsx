import React from 'react';

export interface Column<T> {
  key: string;
  header: string;
  render?: (row: T) => React.ReactNode;
}

export interface TableProps<T> {
  columns: Column<T>[];
  data: T[];
  keyExtractor: (row: T) => string | number;
  className?: string;
}

export function Table<T>({
  columns,
  data,
  keyExtractor,
  className = '',
}: TableProps<T>) {
  return (
    <div className={`table-container ${className}`}>
      <table className="custom-table">
        <thead>
          <tr>
            {columns.map((col) => (
              <th key={col.key}>{col.header}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.length === 0 ? (
            <tr>
              <td colSpan={columns.length} style={{ textAlign: 'center', padding: '32px', color: 'hsl(var(--muted-foreground))' }}>
                No records found.
              </td>
            </tr>
          ) : (
            data.map((row) => (
              <tr key={keyExtractor(row)}>
                {columns.map((col) => (
                  <td key={col.key}>
                    {col.render ? col.render(row) : (row as any)[col.key]}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}
