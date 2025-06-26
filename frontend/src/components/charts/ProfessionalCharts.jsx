/**
 * Professional Chart Components for Advanced Analytics
 * Comprehensive visualization components with export capabilities
 */

import React from "react";
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
} from "recharts";
import {
  Card,
  CardContent,
  CardHeader,
  Typography,
  Box,
  IconButton,
  Menu,
  MenuItem,
} from "@mui/material";
import {
  TrendingUp,
  TrendingDown,
  MoreVert,
  Download,
} from "@mui/icons-material";
import { motion } from "framer-motion";

// Color schemes for different chart types
const COLOR_SCHEMES = {
  primary: ["#1976d2", "#42a5f5", "#90caf9", "#bbdefb"],
  success: ["#388e3c", "#66bb6a", "#a5d6a7", "#c8e6c9"],
  warning: ["#f57c00", "#ffb74d", "#ffcc02", "#ffe082"],
  error: ["#d32f2f", "#ef5350", "#ef9a9a", "#ffcdd2"],
  sentiment: ["#4caf50", "#8bc34a", "#ffc107", "#ff9800", "#f44336"],
  gradient: ["#667eea", "#764ba2", "#f093fb", "#f5576c"],
};

// Professional tooltip component
const ProfessionalTooltip = ({ active, payload, label, formatter }) => {
  if (!active || !payload || !payload.length) return null;

  return (
    <Card
      sx={{
        minWidth: 200,
        boxShadow: 3,
        border: "1px solid rgba(0,0,0,0.1)",
      }}
    >
      <CardContent sx={{ p: 2 }}>
        <Typography variant="subtitle2" gutterBottom>
          {label}
        </Typography>
        {payload.map((entry, index) => (
          <Box
            key={index}
            sx={{ display: "flex", alignItems: "center", mb: 0.5 }}
          >
            <Box
              sx={{
                width: 12,
                height: 12,
                backgroundColor: entry.color,
                borderRadius: "50%",
                mr: 1,
              }}
            />
            <Typography variant="body2">
              {entry.name}: {formatter ? formatter(entry.value) : entry.value}
            </Typography>
          </Box>
        ))}
      </CardContent>
    </Card>
  );
};

// Trend indicator component
const TrendIndicator = ({ trend, value, showValue = true }) => {
  const isPositive = trend === "up" || (typeof trend === "number" && trend > 0);
  const isNegative =
    trend === "down" || (typeof trend === "number" && trend < 0);

  return (
    <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
      {isPositive && (
        <TrendingUp sx={{ color: "success.main", fontSize: 18 }} />
      )}
      {isNegative && (
        <TrendingDown sx={{ color: "error.main", fontSize: 18 }} />
      )}
      {showValue && (
        <Typography
          variant="body2"
          sx={{
            color: isPositive
              ? "success.main"
              : isNegative
                ? "error.main"
                : "text.secondary",
            fontWeight: "medium",
          }}
        >
          {typeof trend === "number"
            ? `${trend > 0 ? "+" : ""}${trend.toFixed(1)}%`
            : value}
        </Typography>
      )}
    </Box>
  );
};

// Professional line chart with trend analysis
export const ProfessionalLineChart = ({
  data,
  title,
  subtitle,
  xKey = "date",
  lines = [],
  height = 300,
  showTrend = true,
  exportable = true,
  onExport,
}) => {
  const [anchorEl, setAnchorEl] = React.useState(null);

  const handleExport = (format) => {
    setAnchorEl(null);
    if (onExport) {
      onExport(format);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Card sx={{ height: "100%" }}>
        <CardHeader
          title={
            <Typography variant="h6" component="div">
              {title}
            </Typography>
          }
          subheader={subtitle}
          action={
            exportable && (
              <>
                <IconButton onClick={(e) => setAnchorEl(e.currentTarget)}>
                  <MoreVert />
                </IconButton>
                <Menu
                  anchorEl={anchorEl}
                  open={Boolean(anchorEl)}
                  onClose={() => setAnchorEl(null)}
                >
                  <MenuItem onClick={() => handleExport("png")}>
                    <Download sx={{ mr: 1 }} /> Export as PNG
                  </MenuItem>
                  <MenuItem onClick={() => handleExport("pdf")}>
                    <Download sx={{ mr: 1 }} /> Export as PDF
                  </MenuItem>
                  <MenuItem onClick={() => handleExport("csv")}>
                    <Download sx={{ mr: 1 }} /> Export Data as CSV
                  </MenuItem>
                </Menu>
              </>
            )
          }
        />
        <CardContent>
          <ResponsiveContainer width="100%" height={height}>
            <LineChart
              data={data}
              margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis
                dataKey={xKey}
                stroke="#666"
                fontSize={12}
                tickLine={false}
              />
              <YAxis
                stroke="#666"
                fontSize={12}
                tickLine={false}
                axisLine={false}
              />
              <Tooltip content={<ProfessionalTooltip />} />
              <Legend />
              {lines.map((line, index) => (
                <Line
                  key={line.key}
                  type="monotone"
                  dataKey={line.key}
                  stroke={
                    line.color ||
                    COLOR_SCHEMES.primary[index % COLOR_SCHEMES.primary.length]
                  }
                  strokeWidth={2}
                  dot={{ fill: line.color, strokeWidth: 2, r: 4 }}
                  activeDot={{ r: 6, strokeWidth: 0 }}
                  name={line.name}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </motion.div>
  );
};

// Professional area chart for metrics over time
export const ProfessionalAreaChart = ({
  data,
  title,
  subtitle,
  xKey = "date",
  areas = [],
  height = 300,
  stacked = false,
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Card sx={{ height: "100%" }}>
        <CardHeader
          title={<Typography variant="h6">{title}</Typography>}
          subheader={subtitle}
        />
        <CardContent>
          <ResponsiveContainer width="100%" height={height}>
            <AreaChart
              data={data}
              margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey={xKey} stroke="#666" fontSize={12} />
              <YAxis stroke="#666" fontSize={12} />
              <Tooltip content={<ProfessionalTooltip />} />
              <Legend />
              {areas.map((area, index) => (
                <Area
                  key={area.key}
                  type="monotone"
                  dataKey={area.key}
                  stackId={stacked ? "1" : undefined}
                  stroke={
                    area.color ||
                    COLOR_SCHEMES.gradient[
                      index % COLOR_SCHEMES.gradient.length
                    ]
                  }
                  fill={
                    area.color ||
                    COLOR_SCHEMES.gradient[
                      index % COLOR_SCHEMES.gradient.length
                    ]
                  }
                  fillOpacity={0.3}
                  name={area.name}
                />
              ))}
            </AreaChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </motion.div>
  );
};

// Professional bar chart with comparison capabilities
export const ProfessionalBarChart = ({
  data,
  title,
  subtitle,
  xKey = "name",
  bars = [],
  height = 300,
  horizontal = false,
}) => {
  const Chart = horizontal ? BarChart : BarChart;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Card sx={{ height: "100%" }}>
        <CardHeader
          title={<Typography variant="h6">{title}</Typography>}
          subheader={subtitle}
        />
        <CardContent>
          <ResponsiveContainer width="100%" height={height}>
            <Chart
              data={data}
              margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
              layout={horizontal ? "horizontal" : "vertical"}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              {horizontal ? (
                <>
                  <XAxis type="number" stroke="#666" fontSize={12} />
                  <YAxis
                    type="category"
                    dataKey={xKey}
                    stroke="#666"
                    fontSize={12}
                  />
                </>
              ) : (
                <>
                  <XAxis dataKey={xKey} stroke="#666" fontSize={12} />
                  <YAxis stroke="#666" fontSize={12} />
                </>
              )}
              <Tooltip content={<ProfessionalTooltip />} />
              <Legend />
              {bars.map((bar, index) => (
                <Bar
                  key={bar.key}
                  dataKey={bar.key}
                  fill={
                    bar.color ||
                    COLOR_SCHEMES.primary[index % COLOR_SCHEMES.primary.length]
                  }
                  name={bar.name}
                  radius={[2, 2, 0, 0]}
                />
              ))}
            </Chart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </motion.div>
  );
};

// Professional pie chart with enhanced styling
export const ProfessionalPieChart = ({
  data,
  title,
  subtitle,
  height = 300,
  showPercent = true,
  innerRadius = 0,
}) => {
  const RADIAN = Math.PI / 180;

  const renderCustomizedLabel = ({
    cx,
    cy,
    midAngle,
    innerRadius,
    outerRadius,
    percent,
  }) => {
    if (!showPercent) return null;

    const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
    const x = cx + radius * Math.cos(-midAngle * RADIAN);
    const y = cy + radius * Math.sin(-midAngle * RADIAN);

    return (
      <text
        x={x}
        y={y}
        fill="white"
        textAnchor={x > cx ? "start" : "end"}
        dominantBaseline="central"
        fontSize={12}
        fontWeight="bold"
      >
        {`${(percent * 100).toFixed(0)}%`}
      </text>
    );
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Card sx={{ height: "100%" }}>
        <CardHeader
          title={<Typography variant="h6">{title}</Typography>}
          subheader={subtitle}
        />
        <CardContent>
          <ResponsiveContainer width="100%" height={height}>
            <PieChart>
              <Pie
                data={data}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={renderCustomizedLabel}
                outerRadius={80}
                innerRadius={innerRadius}
                fill="#8884d8"
                dataKey="value"
              >
                {data.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={
                      entry.color ||
                      COLOR_SCHEMES.sentiment[
                        index % COLOR_SCHEMES.sentiment.length
                      ]
                    }
                  />
                ))}
              </Pie>
              <Tooltip content={<ProfessionalTooltip />} />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </motion.div>
  );
};

// Professional radar chart for relationship health
export const ProfessionalRadarChart = ({
  data,
  title,
  subtitle,
  height = 300,
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Card sx={{ height: "100%" }}>
        <CardHeader
          title={<Typography variant="h6">{title}</Typography>}
          subheader={subtitle}
        />
        <CardContent>
          <ResponsiveContainer width="100%" height={height}>
            <RadarChart
              data={data}
              margin={{ top: 20, right: 80, bottom: 20, left: 80 }}
            >
              <PolarGrid stroke="#e0e0e0" />
              <PolarAngleAxis dataKey="category" tick={{ fontSize: 12 }} />
              <PolarRadiusAxis
                angle={90}
                domain={[0, 100]}
                tick={{ fontSize: 10 }}
                tickCount={6}
              />
              <Radar
                name="Score"
                dataKey="score"
                stroke="#1976d2"
                fill="#1976d2"
                fillOpacity={0.3}
                strokeWidth={2}
              />
              <Tooltip content={<ProfessionalTooltip />} />
            </RadarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </motion.div>
  );
};

// Metric card with trend indicator
export const MetricCard = ({
  title,
  value,
  change,
  trend,
  icon,
  color = "primary",
  subtitle,
  format = "number",
}) => {
  const formatValue = (val) => {
    switch (format) {
      case "percent":
        return `${val}%`;
      case "currency":
        return `$${val.toLocaleString()}`;
      case "time":
        return `${val}m`;
      default:
        return val.toLocaleString();
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
    >
      <Card sx={{ height: "100%", position: "relative" }}>
        <CardContent>
          <Box
            sx={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
            }}
          >
            <Box>
              <Typography variant="h6" component="div" gutterBottom>
                {formatValue(value)}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {title}
              </Typography>
              {subtitle && (
                <Typography variant="caption" color="text.secondary">
                  {subtitle}
                </Typography>
              )}
            </Box>
            <Box
              sx={{
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
              }}
            >
              {icon && <Box sx={{ color: `${color}.main`, mb: 1 }}>{icon}</Box>}
              {(change !== undefined || trend) && (
                <TrendIndicator trend={trend || change} />
              )}
            </Box>
          </Box>
        </CardContent>
      </Card>
    </motion.div>
  );
};

const ProfessionalCharts = {
  ProfessionalLineChart,
  ProfessionalAreaChart,
  ProfessionalBarChart,
  ProfessionalPieChart,
  ProfessionalRadarChart,
  MetricCard,
  TrendIndicator,
};

export default ProfessionalCharts;
