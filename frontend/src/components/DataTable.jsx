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
    <div className="overflow-x-auto rounded-lg border border-gray-200 shadow-sm">
      <table className="w-full border-collapse bg-white">
        <thead>
          <tr className="border-b-2" style={{ background: 'linear-gradient(to right, rgba(241, 90, 42, 0.08), rgba(241, 90, 42, 0.05), rgba(241, 90, 42, 0.08))', borderColor: 'rgba(241, 90, 42, 0.3)' }}>
            {columns.map((column, idx) => (
              <th
                key={idx}
                className={`px-6 py-4 text-left text-xs font-bold uppercase tracking-wider ${
                  idx === 0 ? 'rounded-tl-lg pl-6' : ''
                } ${
                  idx === columns.length - 1 ? 'rounded-tr-lg pr-6' : ''
                }`}
                style={{ minWidth: column.minWidth || 'auto', fontFamily: "'Inter', sans-serif", color: '#3F3F3F' }}
              >
                <div className="flex items-center gap-2">
                  {column.icon && <span style={{ color: '#F15A2A' }}>{column.icon}</span>}
                  {column.label}
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
              className={`transition-all duration-200 ${
                onRowClick ? 'cursor-pointer' : ''
              } ${rowIdx % 2 === 0 ? 'bg-white' : 'bg-gray-50/50'}`}
              style={{
                '&:hover': {
                  background: 'linear-gradient(to right, rgba(241, 90, 42, 0.05), rgba(241, 90, 42, 0.03))'
                }
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = 'linear-gradient(to right, rgba(241, 90, 42, 0.05), rgba(241, 90, 42, 0.03))'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = rowIdx % 2 === 0 ? 'white' : 'rgba(249, 250, 251, 0.5)'
              }}
            >
              {columns.map((column, colIdx) => (
                <td
                  key={colIdx}
                  className={`px-6 py-4 text-sm text-gray-900 ${
                    column.nowrap !== false ? 'whitespace-nowrap' : ''
                  }`}
                >
                  {column.render ? column.render(row[column.key], row) : row[column.key] || '-'}
                </td>
              ))}
            </motion.tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default DataTable

