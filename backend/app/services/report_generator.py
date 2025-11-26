"""Report generation service for evaluation results."""

from typing import Dict, List, Any
from datetime import datetime
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.platypus import Image as RLImage
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

from app.models.evaluation import Evaluation, ZoneStatus
from app.models.heuristic import HeuristicFinding


class ReportGenerator:
    """Service for generating evaluation reports in various formats."""

    def __init__(self, evaluation: Evaluation, findings: List[HeuristicFinding]):
        """Initialize report generator with evaluation data.

        Args:
            evaluation: The evaluation instance
            findings: List of heuristic findings
        """
        self.evaluation = evaluation
        self.findings = findings

    def generate_json_report(self) -> Dict[str, Any]:
        """Generate comprehensive JSON export of evaluation data.

        Returns:
            Complete evaluation data as dictionary
        """
        return {
            "report_metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "report_type": "full_export",
                "format_version": "1.0.0"
            },
            "evaluation": {
                "id": self.evaluation.id,
                "ai_system_name": self.evaluation.ai_system_name,
                "status": self.evaluation.status.value,
                "created_at": self.evaluation.created_at.isoformat(),
                "completed_at": self.evaluation.completed_at.isoformat() if self.evaluation.completed_at else None,
                "iteration_count": self.evaluation.iteration_count,
                "overall_score": self.evaluation.overall_score,
                "zone_status": self.evaluation.zone_status.value if self.evaluation.zone_status else None,
                "heuristic_types": self.evaluation.heuristic_types
            },
            "findings": [
                {
                    "id": finding.id,
                    "heuristic_type": finding.heuristic_type.value,
                    "severity": finding.severity.value,
                    "severity_score": finding.severity_score,
                    "confidence_level": finding.confidence_level,
                    "detection_count": finding.detection_count,
                    "pattern_description": finding.pattern_description,
                    "example_instances": finding.example_instances,
                    "created_at": finding.created_at.isoformat()
                }
                for finding in self.findings
            ],
            "summary": self._generate_summary_data()
        }

    def generate_executive_summary(self) -> Dict[str, Any]:
        """Generate executive summary with key insights.

        Returns:
            Concise summary of key findings and recommendations
        """
        summary_data = self._generate_summary_data()

        return {
            "report_metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "report_type": "executive_summary",
                "format_version": "1.0.0"
            },
            "evaluation_overview": {
                "ai_system_name": self.evaluation.ai_system_name,
                "evaluation_id": self.evaluation.id,
                "evaluation_date": self.evaluation.completed_at.isoformat() if self.evaluation.completed_at else None,
                "overall_score": self.evaluation.overall_score,
                "zone_status": self.evaluation.zone_status.value if self.evaluation.zone_status else None,
                "total_iterations": self.evaluation.iteration_count
            },
            "key_findings": {
                "total_heuristics_detected": len(self.findings),
                "severity_breakdown": summary_data["severity_breakdown"],
                "critical_issues": summary_data["critical_findings_count"],
                "high_priority_issues": summary_data["high_priority_findings_count"]
            },
            "top_concerns": [
                {
                    "heuristic_type": finding.heuristic_type.value,
                    "severity": finding.severity.value,
                    "severity_score": finding.severity_score,
                    "detection_count": finding.detection_count,
                    "pattern_description": finding.pattern_description
                }
                for finding in sorted(self.findings, key=lambda x: x.severity_score, reverse=True)[:3]
            ],
            "risk_assessment": self._generate_risk_assessment(),
            "recommendations": self._generate_high_level_recommendations()
        }

    def generate_pdf_report(self) -> BytesIO:
        """Generate professional PDF report.

        Returns:
            BytesIO buffer containing PDF document
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )

        # Container for PDF elements
        elements = []
        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2C3E50'),
            spaceAfter=30,
            alignment=TA_CENTER
        )

        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#34495E'),
            spaceAfter=12,
            spaceBefore=12
        )

        # Title
        elements.append(Paragraph("AI Bias & Heuristics Evaluation Report", title_style))
        elements.append(Spacer(1, 12))

        # Evaluation Overview Section
        elements.append(Paragraph("Evaluation Overview", heading_style))
        overview_data = [
            ['AI System', self.evaluation.ai_system_name],
            ['Evaluation ID', self.evaluation.id],
            ['Status', self.evaluation.status.value.upper()],
            ['Overall Score', f"{self.evaluation.overall_score:.2f}" if self.evaluation.overall_score else "N/A"],
            ['Zone Status', self._format_zone_status(self.evaluation.zone_status)],
            ['Iterations', str(self.evaluation.iteration_count)],
            ['Created', self.evaluation.created_at.strftime('%Y-%m-%d %H:%M:%S')],
            ['Completed', self.evaluation.completed_at.strftime('%Y-%m-%d %H:%M:%S') if self.evaluation.completed_at else "N/A"]
        ]

        overview_table = Table(overview_data, colWidths=[2*inch, 4*inch])
        overview_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ECF0F1')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#F8F9FA')])
        ]))
        elements.append(overview_table)
        elements.append(Spacer(1, 20))

        # Summary Statistics
        elements.append(Paragraph("Summary Statistics", heading_style))
        summary_data = self._generate_summary_data()

        summary_stats = [
            ['Metric', 'Value'],
            ['Total Findings', str(len(self.findings))],
            ['Critical Issues', str(summary_data['critical_findings_count'])],
            ['High Priority Issues', str(summary_data['high_priority_findings_count'])],
            ['Average Severity Score', f"{summary_data['average_severity_score']:.2f}"],
            ['Average Confidence', f"{summary_data['average_confidence']:.2%}"]
        ]

        summary_table = Table(summary_stats, colWidths=[3*inch, 3*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498DB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8F9FA')])
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 20))

        # Severity Breakdown
        elements.append(Paragraph("Severity Breakdown", heading_style))
        severity_data = [['Severity Level', 'Count']]
        for severity, count in summary_data['severity_breakdown'].items():
            severity_data.append([severity.upper(), str(count)])

        severity_table = Table(severity_data, colWidths=[3*inch, 3*inch])
        severity_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E74C3C')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8F9FA')])
        ]))
        elements.append(severity_table)
        elements.append(Spacer(1, 20))

        # Detailed Findings
        if self.findings:
            elements.append(PageBreak())
            elements.append(Paragraph("Detailed Findings", heading_style))

            for idx, finding in enumerate(sorted(self.findings, key=lambda x: x.severity_score, reverse=True), 1):
                # Finding header
                finding_title = f"{idx}. {finding.heuristic_type.value.replace('_', ' ').title()} - {finding.severity.value.upper()}"
                elements.append(Paragraph(finding_title, styles['Heading3']))

                # Finding details
                finding_data = [
                    ['Severity Score', f"{finding.severity_score:.2f}/100"],
                    ['Confidence Level', f"{finding.confidence_level:.2%}"],
                    ['Detection Count', str(finding.detection_count)],
                    ['Pattern Description', finding.pattern_description]
                ]

                finding_table = Table(finding_data, colWidths=[2*inch, 4*inch])
                finding_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ECF0F1')),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP')
                ]))
                elements.append(finding_table)
                elements.append(Spacer(1, 12))

        # Risk Assessment
        elements.append(PageBreak())
        elements.append(Paragraph("Risk Assessment", heading_style))
        risk_assessment = self._generate_risk_assessment()
        risk_text = f"""
        <b>Overall Risk Level:</b> {risk_assessment['risk_level']}<br/>
        <b>Assessment:</b> {risk_assessment['assessment']}<br/><br/>
        <b>Key Concerns:</b><br/>
        {risk_assessment['key_concerns']}
        """
        elements.append(Paragraph(risk_text, styles['BodyText']))
        elements.append(Spacer(1, 20))

        # Recommendations
        elements.append(Paragraph("Recommendations", heading_style))
        recommendations = self._generate_high_level_recommendations()
        for rec in recommendations:
            rec_text = f"• <b>{rec['priority']}:</b> {rec['recommendation']}"
            elements.append(Paragraph(rec_text, styles['BodyText']))
            elements.append(Spacer(1, 8))

        # Footer
        elements.append(Spacer(1, 30))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER
        )
        footer_text = f"Generated on {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC | AI Bias & Heuristics Diagnostic Tool"
        elements.append(Paragraph(footer_text, footer_style))

        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer

    def _generate_summary_data(self) -> Dict[str, Any]:
        """Generate summary statistics from findings."""
        if not self.findings:
            return {
                "severity_breakdown": {},
                "critical_findings_count": 0,
                "high_priority_findings_count": 0,
                "average_severity_score": 0.0,
                "average_confidence": 0.0
            }

        severity_breakdown = {}
        for finding in self.findings:
            severity = finding.severity.value
            severity_breakdown[severity] = severity_breakdown.get(severity, 0) + 1

        critical_count = sum(1 for f in self.findings if f.severity.value == 'critical')
        high_count = sum(1 for f in self.findings if f.severity.value == 'high')

        avg_severity = sum(f.severity_score for f in self.findings) / len(self.findings)
        avg_confidence = sum(f.confidence_level for f in self.findings) / len(self.findings)

        return {
            "severity_breakdown": severity_breakdown,
            "critical_findings_count": critical_count,
            "high_priority_findings_count": high_count,
            "average_severity_score": avg_severity,
            "average_confidence": avg_confidence
        }

    def _generate_risk_assessment(self) -> Dict[str, str]:
        """Generate overall risk assessment."""
        if not self.evaluation.zone_status:
            return {
                "risk_level": "UNKNOWN",
                "assessment": "Evaluation not completed",
                "key_concerns": "No data available"
            }

        zone = self.evaluation.zone_status
        score = self.evaluation.overall_score or 0

        if zone == ZoneStatus.GREEN:
            risk_level = "LOW"
            assessment = f"The AI system shows minimal bias patterns with an overall score of {score:.2f}. The system is operating within acceptable parameters."
        elif zone == ZoneStatus.YELLOW:
            risk_level = "MODERATE"
            assessment = f"The AI system shows concerning bias patterns with an overall score of {score:.2f}. Immediate attention and corrective measures are recommended."
        else:  # RED
            risk_level = "HIGH"
            assessment = f"The AI system shows critical bias patterns with an overall score of {score:.2f}. Urgent intervention required to address systematic issues."

        # Generate key concerns
        critical_findings = [f for f in self.findings if f.severity.value in ['critical', 'high']]
        if critical_findings:
            concerns = "<br/>".join([
                f"• {f.heuristic_type.value.replace('_', ' ').title()}: {f.pattern_description}"
                for f in critical_findings[:3]
            ])
        else:
            concerns = "No critical concerns identified."

        return {
            "risk_level": risk_level,
            "assessment": assessment,
            "key_concerns": concerns
        }

    def _generate_high_level_recommendations(self) -> List[Dict[str, str]]:
        """Generate high-level recommendations based on findings."""
        recommendations = []

        if not self.findings:
            return [{
                "priority": "INFO",
                "recommendation": "Continue monitoring the AI system for potential bias patterns."
            }]

        critical_findings = [f for f in self.findings if f.severity.value == 'critical']
        high_findings = [f for f in self.findings if f.severity.value == 'high']

        if critical_findings:
            recommendations.append({
                "priority": "URGENT",
                "recommendation": f"Address {len(critical_findings)} critical bias pattern(s) immediately. Consider suspending the AI system until issues are resolved."
            })

        if high_findings:
            recommendations.append({
                "priority": "HIGH",
                "recommendation": f"Investigate and remediate {len(high_findings)} high-severity bias pattern(s) within the next review cycle."
            })

        # Specific heuristic-based recommendations
        heuristic_types = set(f.heuristic_type.value for f in self.findings)

        if 'anchoring' in heuristic_types:
            recommendations.append({
                "priority": "MEDIUM",
                "recommendation": "Review training data for anchoring bias. Consider implementing reference point randomization."
            })

        if 'confirmation_bias' in heuristic_types:
            recommendations.append({
                "priority": "MEDIUM",
                "recommendation": "Implement adversarial testing to challenge confirmation bias patterns in the AI system."
            })

        if not recommendations:
            recommendations.append({
                "priority": "LOW",
                "recommendation": "Maintain current monitoring protocols and conduct regular bias assessments."
            })

        return recommendations

    def _format_zone_status(self, zone_status) -> str:
        """Format zone status with color indicator."""
        if not zone_status:
            return "N/A"

        status_map = {
            ZoneStatus.GREEN: "GREEN (Acceptable)",
            ZoneStatus.YELLOW: "YELLOW (Warning)",
            ZoneStatus.RED: "RED (Critical)"
        }
        return status_map.get(zone_status, zone_status.value.upper())
