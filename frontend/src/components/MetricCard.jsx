import React from 'react';

const MetricCard = ({ label, value, icon }) => (
  <div className="bg-[#f2f2f2] md:bg-white rounded-[2rem] md:rounded-2xl p-4 md:p-6 flex items-center shadow-sm hover:shadow-md transition-shadow cursor-default border border-transparent md:border-gray-100">
    <div className="mr-4 pl-2 md:bg-gray-50 md:p-3 md:rounded-xl">
      {icon}
    </div>
    <div className="flex flex-col">
      <span className="text-[10px] md:text-xs font-bold text-gray-500 uppercase tracking-widest font-sans mb-1">
        {label}
      </span>
      <span className="text-2xl md:text-3xl text-gray-600 font-mono tracking-tighter font-medium">
        {value}
      </span>
    </div>
  </div>
);

export default MetricCard;