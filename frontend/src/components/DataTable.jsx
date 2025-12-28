import { motion } from 'framer-motion'

const DataTable = ({ 
  columns, 
  data, 
  onRowClick, 
  emptyMessage = "No data available",
  loading = false 
}) => {
  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2" style={{ borderColor: '#F15A2A' }}></div>
      </div>
    )
  }

  if (!data || data.length === 0) {
    return (
      <div className="card-3d p-8 text-center">
        <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
        </svg>
        <p className="text-gray-600">{emptyMessage}</p>
      </div>
    )
  }

  return (
    <div className="rounded-xl border border-gray-200 shadow-lg overflow-hidden bg-white">
      <div className="overflow-y-auto overflow-x-hidden max-h-[calc(100vh-250px)]">
        <table className="w-full border-collapse bg-white table-fixed">
          <thead className="sticky top-0 z-10">
            <tr className="border-b-2" style={{ 
              background: 'linear-gradient(to right, rgba(241, 90, 42, 0.12), rgba(241, 90, 42, 0.08), rgba(241, 90, 42, 0.12))', 
              borderColor: 'rgba(241, 90, 42, 0.2)',
              boxShadow: '0 2px 4px rgba(0,0,0,0.05)'
            }}>
              {columns.map((column, idx) => (
                <th
                  key={idx}
                  className={`px-4 py-4 text-center text-xs font-bold uppercase tracking-wider ${
                    idx === 0 ? 'rounded-tl-xl pl-6' : ''
                  } ${
                    idx === columns.length - 1 ? 'rounded-tr-xl pr-6' : ''
                  }`}
                  style={{ 
                    width: column.width || 'auto',
                    minWidth: column.minWidth || 'auto',
                    maxWidth: column.maxWidth || 'none',
                    fontFamily: "'Inter', sans-serif", 
                    color: '#3F3F3F',
                    letterSpacing: '0.05em'
                  }}
                >
                  <div className="flex items-center justify-center gap-1.5">
                    {column.icon && <span style={{ color: '#F15A2A' }}>{column.icon}</span>}
                    <span className="truncate">{column.label}</span>
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-100">
            {data.map((row, rowIdx) => (
              <motion.tr
                key={row.id || rowIdx}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: rowIdx * 0.03 }}
                onClick={() => onRowClick && onRowClick(row)}
                className={`transition-all duration-200 border-b border-gray-100 ${
                  onRowClick ? 'cursor-pointer' : ''
                } ${rowIdx % 2 === 0 ? 'bg-white' : 'bg-gray-50/30'}`}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = 'linear-gradient(to right, rgba(241, 90, 42, 0.08), rgba(241, 90, 42, 0.05), rgba(241, 90, 42, 0.08))'
                  e.currentTarget.style.transform = 'scale(1.01)'
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = rowIdx % 2 === 0 ? 'white' : 'rgba(249, 250, 251, 0.3)'
                  e.currentTarget.style.transform = 'scale(1)'
                }}
              >
                {columns.map((column, colIdx) => (
                  <td
                    key={colIdx}
                    className={`px-4 py-4 text-sm text-gray-900 text-center ${
                      column.nowrap !== false ? 'whitespace-nowrap' : ''
                    }`}
                    style={{
                      width: column.width || 'auto',
                      minWidth: column.minWidth || 'auto',
                      maxWidth: column.maxWidth || 'none',
                      fontFamily: "'Inter', sans-serif"
                    }}
                  >
                    <div className="flex items-center justify-center">
                      {column.render ? column.render(row[column.key], row) : row[column.key] || '-'}
                    </div>
                  </td>
                ))}
              </motion.tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default DataTable

